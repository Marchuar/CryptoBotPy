from telegram import Bot
import ccxt
import pandas
import talib
import time

exchange = ccxt.bybit()
bot = Bot("***REMOVED_TG_TOKEN***")

symbol = "BTCUSDT"
timeframe = "1m"

EMA_long_2 = [0]
EMA_short_2 = [0]


def fetchData(userIds, limit=150):
    while True:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        dataFrame = pandas.DataFrame(
            ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

        signal = startAnalyze(dataFrame)
        print(signal)

        if signal:
            for chatId in userIds:
                bot.send_message(chat_id=chatId, text=signal)

        time.sleep(60)


def startAnalyze(
    df, short_ema=50, long_ema=100, rsi_period=14, rsi_overbought=70, rsi_oversold=30
):
    print(df)
    df["EMA_short"] = talib.EMA(df["close"], timeperiod=short_ema)
    df["EMA_long"] = talib.EMA(df["close"], timeperiod=long_ema)
    # df["RSI"] = talib.RSI(df["close"], timeperiod=rsi_period)

    if len(df) < long_ema:  # Убедитесь, что достаточно данных
        return None

    ema_signal = None

    print("EMA_short -2: " + str(EMA_short_2[0]))
    print("EMA_long -2: " + str(EMA_long_2[0]))

    print("EMA_short -1: " + str(df["EMA_short"].iloc[-1]))
    print("EMA_long -1: " + str(df["EMA_long"].iloc[-1]))

    if (
        EMA_short_2[0] < EMA_long_2[0]
        and df["EMA_short"].iloc[-1] > df["EMA_long"].iloc[-1]
    ):
        ema_signal = "long"
    elif (
        EMA_short_2[0] > EMA_long_2[0]
        and df["EMA_short"].iloc[-1] < df["EMA_long"].iloc[-1]
    ):
        ema_signal = "short"

    EMA_short_2.clear()
    EMA_long_2.clear()
    EMA_short_2.append(df["EMA_short"].iloc[-1])
    EMA_long_2.append(df["EMA_long"].iloc[-1])

    return ema_signal

    # if ema_signal == "long" and df["RSI"].iloc[-1] < rsi_oversold:
    # return "long"
    # elif ema_signal == "short" and df["RSI"].iloc[-1] > rsi_overbought:
    # return "short"
    # return None
