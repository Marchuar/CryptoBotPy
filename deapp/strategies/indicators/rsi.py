import talib


class RSIStrategy:
    def __init__(self, rsi_overbought=70, rsi_oversold=30, rsi_period=14):
        self.name = "RSI"
        self.candles_amount = rsi_period * 2
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        print(f"Generate signal for {self.name} strategy")

        curr_rsi = df["RSI"].iloc[-1]

        if (
                curr_rsi < self.rsi_oversold
        ):
            print(f"Signal for {self.name}: long")
            return "long"
        elif (
                curr_rsi > self.rsi_overbought
        ):
            print(f"Signal for {self.name}: short")
            return "short"

        print(f"Signal for {self.name}: no_signal")
        return "no_signal"

    def calculate_indicators(self, df):
        # Указываем индикаторы
        print("....")
        print(f"Calculate indicators for: {self.name} strategy")
        df["RSI"] = talib.RSI(df["close"], timeperiod=self.rsi_period)
        return df
