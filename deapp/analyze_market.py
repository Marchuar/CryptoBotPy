import asyncio
import json
import logging
from datetime import datetime
from constants import DEFAULT_ANALYZE_INTERVAL
from sql.commands import db_get_subscribed_users, tg_get_user_timeframe
from strategies.universal import UniversalStrategy
import pandas as pd


async def start_analyze(bot, exchange, state):
    while True:
        try:
            logging.info("Starting market analysis...")
            subscribed_users = db_get_subscribed_users()

            tasks = []
            if subscribed_users:
                for user_id in subscribed_users:
                    task = asyncio.create_task(
                        analyze_market(user_id, tg_get_user_timeframe(user_id), bot, exchange, state)
                    )
                    tasks.append(task)

                await asyncio.gather(*tasks, return_exceptions=True)

                logging.info(f"Market analysis completed. Waiting for {DEFAULT_ANALYZE_INTERVAL} seconds...")
                await asyncio.sleep(DEFAULT_ANALYZE_INTERVAL)
            else:
                logging.info("No subs, skip analyze")
                await asyncio.sleep(DEFAULT_ANALYZE_INTERVAL)
        except Exception as e:
            logging.error(f"Error in market analysis: {e}")
            await asyncio.sleep(DEFAULT_ANALYZE_INTERVAL)


async def analyze_market(user_id, timeframe, bot, exchange, state,
                         strategy=UniversalStrategy()):

    #async with state.lock:
        filtered_symbols = list(state.markets.keys())
        for symbol in filtered_symbols:
            try:
                start = datetime.now()
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=strategy.candles_amount)

                if not ohlcv or len(ohlcv) < strategy.candles_amount:
                    logging.warning(f"Недостаточно данных для символа {symbol}. Пропускаем...")
                    continue

                df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
                if df.empty or df.shape[0] < strategy.candles_amount:
                    logging.warning(f"DataFrame пуст или данных недостаточно для символа {symbol}. Пропускаем...")
                    continue

                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

                logging.info(f"Начало анализа для символа: {symbol}")
                signal = strategy.generate_signal(strategy.calculate_indicators(df))

                logging.info(f"Результат: стратегия {strategy.name[0]}, сигнал: {signal}")
                logging.info(f"Время анализа: {(datetime.now() - start)}")

                if signal and signal != "no_signal":
                    message = {
                        "exchange": exchange.id,
                        "symbol": symbol,
                        "strategy": strategy.name,
                        "timeframe": timeframe,
                        "signal": signal,
                    }
                    # TODO вынести бы это куда-то + передавать более красивое сообщение
                    await bot.send_message(chat_id=user_id, text=json.dumps(message, indent=2))

            except Exception as e:
                logging.error(f"Ошибка обработки символа {symbol}: {e}")
