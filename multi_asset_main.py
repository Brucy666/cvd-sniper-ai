# multi_asset_main.py

from bybit_feed import BybitFeed
from cvd_engine import CVDEngine
from cvd_multi_tf_engine import MultiTimeframeCVDEngine
from multi_tf_divergence_matrix import detect_multi_tf_divergence_matrix
from cvd_ai_score import score_cvd_signal_from_matrix
from cvd_memory_store import CVDMemoryStore
from discord_notifier import send_discord_alert
from cvd_backfill import backfill_cvd
from trap_cooldown import should_alert
import asyncio

WATCH_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
MAX_HISTORY = 30

async def start_sniper(symbol):
    print(f"🚀 Starting sniper engine for {symbol}")

    # Initialize engines
    cvd = CVDEngine()
    multi_cvd = MultiTimeframeCVDEngine()
    memory = CVDMemoryStore()
    price_history = []

    # Preload historical CVD and price memory
    print(f"🧠 Backfilling CVD for {symbol}")
    price_data_map, cvd_data_map = backfill_cvd(symbol)

    for tf in cvd_data_map:
        multi_cvd.cvd_history[tf] = cvd_data_map[tf]
        if tf == "1m":
            price_history = price_data_map[tf][-MAX_HISTORY:]
        print(f"✅ Loaded {tf} CVD history ({len(cvd_data_map[tf])} pts)")

    async def on_tick(data):
        # Update live CVD
        cvd_value = cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
        multi_cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])

        # Update price history
        price_history.append(data["price"])
        if len(price_history) > MAX_HISTORY:
            price_history.pop(0)

        # Use same price history across TFs for now
        price_data_map_live = {
            "1m": price_history,
            "3m": price_history,
            "5m": price_history,
            "15m": price_history
        }

        divergence_matrix = detect_multi_tf_divergence_matrix(price_data_map_live, multi_cvd, lookback=5)
        print(f"[{symbol}] 📊 Matrix: {divergence_matrix}")

        vwap_relation = "failing reclaim"
        delta_behavior = "spike_no_follow"
        result = score_cvd_signal_from_matrix(divergence_matrix, vwap_relation, delta_behavior)

        # Cooldown filtering
        if result["score"] > 60 and should_alert(symbol, data["price"], divergence_matrix):
            print(f"🚨 SNIPER TRAP [{symbol}] | Score: {result['score']}")
            memory.log_event(data["timestamp"], cvd_value, data["price"], divergence_matrix, result["score"])
            send_discord_alert(symbol, result, data["price"], divergence_matrix)
        else:
            print(f"[{symbol}] ↪ No sniper trap | Score: {result['score']}")

    # Launch Bybit feed
    feed = BybitFeed(symbol=symbol)
    await feed.connect(on_tick)

async def main():
    await asyncio.gather(*[start_sniper(symbol) for symbol in WATCH_SYMBOLS])

if __name__ == "__main__":
    asyncio.run(main())
