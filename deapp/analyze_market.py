from telegram.ext import ContextTypes
from bot import bot, user_ids_ema, user_ids_bb, user_ids_macd
from connect import get_connection
from market_filter.filter_for_strategy import filter_symbols_for_strategy
from market_filter.market_item_type import get_perpetual
import pandas as pd

DEFAULT_SYMBOLS = ["ETHUSDT", "BNBUSDT"]


async def analyze_market(context: ContextTypes.DEFAULT_TYPE, exchange=get_connection("bybit"), symbols=DEFAULT_SYMBOLS,
                         timeframe="1m", all_symbols_mode=False):
    # Получаем стратегию
    strategy = context.job.data

    # Достаем все символы и фильтруем их, если режим включен
    if all_symbols_mode:
        symbols = get_perpetual(exchange)
        symbols = filter_symbols_for_strategy(exchange, symbols, timeframe, strategy.candles_amount)

    for symbol in symbols:
        try:
            # Получаем данные из биржи
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=strategy.candles_amount)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

            # Расчитываем индикаторы и генерируем сигнал
            print("----------------------------------------")
            print(f"Start analyze for symbol: {symbol}")
            signal = strategy.generate_signal(
                strategy.calculate_indicators(df)
            )  # Добавить обработчик недостаточного кол-ва свечей

            print("...\nResult >>>>")
            print(strategy.name + f" signal: \"{signal}\"")
            if signal and signal != "no_signal":
                message = {
                    "exchange": exchange.id,
                    "symbol": symbol,
                    "strategy": strategy.name,
                    "timeframe": timeframe,
                    "signal": signal,
                }

                if strategy.name == "EMA/RSI/ATR":
                    for user_id in user_ids_ema:
                        await bot.send_message(chat_id=user_id, text=message)
                elif strategy.name == "BB/RSI/ATR":
                    for user_id in user_ids_bb:
                        await bot.send_message(chat_id=user_id, text=message)
                elif strategy.name == "MACD/RSI/ATR":
                    for user_id in user_ids_macd:
                        await bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            print(f"Ошибка обработки символа: {symbol}: {e}")
