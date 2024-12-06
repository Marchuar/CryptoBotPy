import talib


class EMAStrategy:
    def __init__(self, short_ema=50, long_ema=100):
        self.name = "EMA/RSI"
        self.candles_amount = max(short_ema, long_ema)
        self.short_ema = short_ema
        self.long_ema = long_ema
        self.short_ema_prev = 0
        self.long_ema_prev = 0

    def generate_signal(self, df, rsi_overbought=50, rsi_oversold=50):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        prev_short = self.short_ema_prev
        prev_long = self.long_ema_prev
        curr_short = df["EMA_short"].iloc[-1]
        curr_long = df["EMA_long"].iloc[-1]

        curr_rsi = df["RSI"].iloc[-1]
        print(curr_rsi)

        if (
            prev_short < prev_long
            and curr_short > curr_long
            and curr_rsi < rsi_oversold
        ):
            self.short_ema_prev = curr_short
            self.long_ema_prev = curr_long
            return "long"
        elif (
            prev_short > prev_long
            and curr_short < curr_long
            and curr_rsi > rsi_overbought
        ):
            self.short_ema_prev = curr_short
            self.long_ema_prev = curr_long
            return "short"

        self.short_ema_prev = curr_short
        self.long_ema_prev = curr_long
        return "no_signal"


    def calculate_indicators(self, df, rsi_period=14):
        # Указываем индикаторы
        df["EMA_short"] = talib.EMA(df["close"], timeperiod=self.short_ema)
        df["EMA_long"] = talib.EMA(df["close"], timeperiod=self.long_ema)
        df["RSI"] = talib.RSI(df["close"], timeperiod=rsi_period)
        print(df)
        return df
