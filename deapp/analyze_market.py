from bot import bot, userIds
from connect import get_connection
import pandas as pd
import time


def analyze_market(strategy,
                   exchange=get_connection("bybit"),
                   symbol="BTCUSDT",
                   timeframe="1m"):
    while True:
        # Получаем данные из биржи
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=strategy.candles_amount)
        df = pd.DataFrame(
            ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Расчитываем индикаторы и генерируем сигнал
        signal = strategy.generate_signal(strategy.calculate_indicators(
            df
        ))  # Добавить обработчик недостаточного кол-ва свечей

        print(f"Сигнал: {signal}")
        if signal and signal != "no_signal":
            message = {
                "exchange": exchange.id,
                "symbol": symbol,
                "strategy": strategy.name,
                "timeframe": timeframe,
                "signal": signal,
            }

            for user_id in userIds:
                bot.send_message(chat_id=user_id, text=message)
        time.sleep(15)
