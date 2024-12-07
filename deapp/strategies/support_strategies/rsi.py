import talib


class RSIStrategy:
    def __init__(self, rsi_overbought=60, rsi_oversold=40, rsi_period=14):
        self.name = "RSI"
        self.candles_amount = rsi_period * 2
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        curr_rsi = df["RSI"].iloc[-1]
        print(curr_rsi)

        if (
            curr_rsi < self.rsi_oversold
        ):
            return "long"
        elif (
            curr_rsi > self.rsi_overbought
        ):
            return "short"

        return "no_signal"


    def calculate_indicators(self, df):
        # Указываем индикаторы
        df["RSI"] = talib.RSI(df["close"], timeperiod=self.rsi_period)
        return df