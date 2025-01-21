import logging
from datetime import datetime
from main import bot
from connect import get_connection
from constants import DEFAULT_ANALYZE_ALL_SYMBOLS_MODE, DEFAULT_ANALYZE_SYMBOLS
from market_filter.filter_for_strategy import filter_symbols_for_strategy
from market_filter.market_item_type import get_perpetual
from strategies.universal import UniversalStrategy
import pandas as pd


async def analyze_market(user_id, timeframe,
                         strategy=UniversalStrategy(),
                         exchange=get_connection("bybit"),
                         symbols=DEFAULT_ANALYZE_SYMBOLS,
                         all_symbols_mode=DEFAULT_ANALYZE_ALL_SYMBOLS_MODE):

    # Достаем все символы и фильтруем их, если режим включен
    if all_symbols_mode:
        symbols = get_perpetual(exchange)
        symbols = filter_symbols_for_strategy(exchange, symbols, timeframe, strategy.candles_amount)

    for symbol in symbols:
        try:
            # Получаем данные из биржи
            start = datetime.now()
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=strategy.candles_amount)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

            # Расчитываем индикаторы и генерируем сигнал
            logging.info(f"\n----------------------------------------\nStart analyze for symbol: {symbol}")
            signal = strategy.generate_signal(
                strategy.calculate_indicators(df)
            )
            logging.info("...\nResult >>>>")
            logging.info(strategy.name[0] + f", signal: \"{signal}\"")
            logging.info(f"Analyze took: {(datetime.now() - start)}")

            #if signal and signal != "no_signal":
            message = {
                "exchange": exchange.id,
                "symbol": symbol,
                "strategy": strategy.name,
                "timeframe": timeframe,
                "signal": signal,
            }
            await bot.send_message(chat_id=user_id, text=message)

        except Exception as e:
            logging.error(f"Ошибка обработки символа: {symbol}: {e}")
