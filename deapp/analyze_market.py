import asyncio
import logging
from datetime import datetime

from bot import send_signal_message, analyze_notify
from constants import DEFAULT_ANALYZE_INTERVAL
from sql.commands import db_get_subscribed_users, tg_get_user_timeframe
from strategies.universal import UniversalStrategy
import pandas as pd


async def start_analyze(exchange, state):
    while True:
        try:
            logging.info("Starting market analysis...")
            subscribed_users = db_get_subscribed_users()

            tasks = []
            if subscribed_users:
                for user_id in subscribed_users:
                    await analyze_notify(user_id, "start")
                    task = asyncio.create_task(
                        analyze_market(user_id, tg_get_user_timeframe(user_id), exchange, state)
                    )
                    tasks.append(task)
                await asyncio.gather(*tasks, return_exceptions=True)

                logging.info(f"Market analysis completed. Waiting for {DEFAULT_ANALYZE_INTERVAL} seconds...")
                for user_id in subscribed_users:
                    await analyze_notify(user_id, "stop")
                await asyncio.sleep(DEFAULT_ANALYZE_INTERVAL)
            else:
                logging.info("No subs, skip analyze")
                await asyncio.sleep(DEFAULT_ANALYZE_INTERVAL)
        except Exception as e:
            logging.error(f"Error in market analysis: {e}")
            await asyncio.sleep(DEFAULT_ANALYZE_INTERVAL)


async def analyze_market(user_id, timeframe, exchange, state,
                         strategy=UniversalStrategy()):
    filtered_symbols = list(state.markets.keys())
    for symbol in filtered_symbols:
        try:
            start = datetime.now()
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=strategy.candles_amount)

            if not ohlcv or len(ohlcv) < strategy.candles_amount:
                logging.warning(f"Not enough data for symbol {symbol}. Skip...")
                continue

            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            if df.empty or df.shape[0] < strategy.candles_amount:
                logging.warning(f"DataFrame is empty or there is not enough data for the symbol {symbol}. Skip...")
                continue

            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

            logging.info(f"Beginning analysis for the symbol: {symbol}")
            signal = strategy.generate_signal(strategy.calculate_indicators(df))

            logging.info(f"Result: strategy  {strategy.name[0]}, signal: {signal}")
            logging.info(f"Analysis time: {(datetime.now() - start)}")

            if signal and signal != "no_signal":
                await send_signal_message(user_id, exchange.id, symbol, strategy.name, timeframe, signal)

        except Exception as e:
            logging.error(f"Symbol processing error {symbol}: {e}")
