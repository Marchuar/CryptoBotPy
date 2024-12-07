from telegram.ext import ContextTypes

from bot import bot, user_ids
from connect import get_connection
import pandas as pd

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

    print(f"BB Signal: {signal}")
    if signal and signal != "no_signal":
        message = {
            "exchange": exchange.id,
            "symbol": symbol,
            "strategy": strategy.name,
            "timeframe": timeframe,
            "signal": signal,
        }

        for user_id in user_ids:
            await bot.send_message(chat_id=user_id, text=message)
