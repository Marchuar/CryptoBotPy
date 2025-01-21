import json
import logging
from datetime import datetime
from connect import get_connection
from constants import DEFAULT_ANALYZE_ALL_SYMBOLS_MODE, DEFAULT_ANALYZE_SYMBOLS
from market_filter.filter_for_strategy import filter_symbols_for_strategy
from market_filter.market_item_type import get_perpetual
from strategies.universal import UniversalStrategy
import pandas as pd


async def analyze_market(user_id, timeframe, bot,
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
                #TODO вынести бы это куда-то + передавать более красивое сообщение
                await bot.send_message(chat_id=user_id, text=json.dumps(message, indent=2))

        except Exception as e:
            logging.error(f"Ошибка обработки символа {symbol}: {e}")
