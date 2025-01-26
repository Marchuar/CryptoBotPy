import logging
from datetime import datetime

from connect import get_connection
from constants import DEFAULT_ANALYZE_ALL_SYMBOLS_MODE, DEFAULT_ANALYZE_SYMBOLS
from market_filter.filter_for_strategy import filter_symbols_for_strategy
from market_filter.market_item_type import get_perpetual
from strategies.universal import UniversalStrategy
import pandas as pd
from bot import send_signal_message

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
            start = datetime.now()
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=strategy.candles_amount)

            if not ohlcv or len(ohlcv) < strategy.candles_amount:
                logging.warning(f"Not enough data for the symbol {symbol}. Skip...")
                continue

            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            if df.empty or df.shape[0] < strategy.candles_amount:
                logging.warning(f"DataFrame is empty or there is not enough data for the symbol {symbol}. Skip...")
                continue

            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

            logging.info(f"Beginning analysis for the symbol: {symbol}")
            signal = strategy.generate_signal(strategy.calculate_indicators(df))

            logging.info(f"Result: strategy {strategy.name[0]}, signal: {signal}")
            logging.info(f"Analysis time: {(datetime.now() - start)}")

            #if signal and signal != "no_signal":
            await send_signal_message(user_id, exchange.id, symbol, strategy.name, timeframe, signal)

        except Exception as e:
            logging.error(f"Symbol processing error {symbol}: {e}")
