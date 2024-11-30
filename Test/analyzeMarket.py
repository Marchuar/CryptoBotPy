from telegram import Bot
import ccxt
import pandas
import talib
import time

exchange = ccxt.bybit()
bot = Bot("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c")

symbol = "BTC/USDT"
timeframe = "1m"


def fetchData(userIds, limit=50):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    dataFrame = pandas.DataFrame(
        ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )

    while True:
        signal = startAnalyze(dataFrame)

        if signal:
            for chatId in userIds:
                bot.send_message(chat_id=chatId, text=signal)

        time.sleep(10)


def startAnalyze(
    df, short_ema=50, long_ema=100, rsi_period=14, rsi_overbought=70, rsi_oversold=30
):
    df["EMA_short"] = talib.EMA(df["close"], timeperiod=short_ema)
    df["EMA_long"] = talib.EMA(df["close"], timeperiod=long_ema)
    df["RSI"] = talib.RSI(df["close"], timeperiod=rsi_period)

    ema_signal = None
    if (
        df["EMA_short"].iloc[-2] < df["EMA_long"].iloc[-2]
        and df["EMA_short"].iloc[-1] > df["EMA_long"].iloc[-1]
    ):
        ema_signal = "long"
    elif (
        df["EMA_short"].iloc[-2] > df["EMA_long"].iloc[-2]
        and df["EMA_short"].iloc[-1] < df["EMA_long"].iloc[-1]
    ):
        ema_signal = "short"

    if ema_signal == "long" and df["RSI"].iloc[-1] < rsi_oversold:
        return "long"
    elif ema_signal == "short" and df["RSI"].iloc[-1] > rsi_overbought:
        return "short"
    return None
