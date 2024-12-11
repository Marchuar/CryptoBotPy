from telegram.ext import ContextTypes

from bot import bot, user_ids_ema, user_ids_bb, user_ids_macd
from connect import get_connection
import pandas as pd

from strategies.support_strategies.rsi import RSIStrategy
from strategies.support_strategies.atr import ATRStrategy


async def analyze_market(context: ContextTypes.DEFAULT_TYPE, exchange=get_connection("bybit"), symbol="ETHUSDT", timeframe="1m"):

    # Получаем стратегию
    strategy = context.job.data

    # Получаем данные из биржи
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=strategy.candles_amount)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # Расчитываем индикаторы и генерируем сигнал
    signal = strategy.generate_signal(
        strategy.calculate_indicators(df)
    )  # Добавить обработчик недостаточного кол-ва свечей
    print(strategy.name + f" Signal: {signal}")

    # Определяем вспомогательные стратегии
    rsi_strategy = RSIStrategy()
    rsi_signal = rsi_strategy.generate_signal(rsi_strategy.calculate_indicators(df))
    print("RSI signal: " + str(rsi_signal))

    atr_strategy = ATRStrategy()
    atr_signal = atr_strategy.generate_signal(atr_strategy.calculate_indicators(df))
    print("ATR signal: " + str(atr_signal))

    # Проверяем сигналы с вспомогательных стратегий
    if signal == "long" and rsi_signal == "long" and atr_signal == "true":
        signal = "long"
    elif signal == "short" and rsi_signal == "short" and atr_signal == "true":
        signal = "short"
    else:
        signal = "no_signal"

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
