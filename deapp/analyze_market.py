from telegram.ext import ContextTypes

from bot import bot, user_ids_ema, user_ids_bb, user_ids_macd
from connect import get_connection
import pandas as pd

DEFAULT_SYMBOLS = ["ETHUSDT", "BNBUSDT"]


async def analyze_market(context: ContextTypes.DEFAULT_TYPE, exchange=get_connection("bybit"), symbols=DEFAULT_SYMBOLS,
                         timeframe="1m", all_symbols_mode=False):
    # Получаем стратегию
    strategy = context.job.data
    atr_strategy = ATRStrategy()
    rsi_strategy = RSIStrategy()

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

            rsi_signal = rsi_strategy.generate_signal(rsi_strategy.calculate_indicators(df))
            print("RSI signal: " + str(rsi_signal))

            atr_signal = atr_strategy.generate_signal(atr_strategy.calculate_indicators(df))
            print("ATR signal: " + str(atr_signal))

            # Проверяем сигналы с вспомогательных стратегий
            if signal == "long" and rsi_signal == "long" and atr_signal == "true":
                signal = "long"
            elif signal == "short" and rsi_signal == "short" and atr_signal == "true":
                signal = "short"
            else:
                signal = "no_signal"

            print("...\nResult >>>>")
            print(strategy.name + f" with RSI/ATR, signal: \"{signal}\"")
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
