import talib

from strategies.support_strategies import ATRStrategy, RSIStrategy


class EMAStrategy:
    def __init__(self, short_ema=50, long_ema=100):
        self.name = "EMA_with_RSI_and_ATR"
        self.candles_amount = max(short_ema, long_ema)
        self.short_ema = short_ema
        self.long_ema = long_ema
        self.short_ema_prev = 0
        self.long_ema_prev = 0
        self.atr_strategy = ATRStrategy()
        self.rsi_strategy = RSIStrategy()

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        print(f"Generate signal for {self.name} strategy")

        prev_short = self.short_ema_prev
        prev_long = self.long_ema_prev
        curr_short = df["EMA_short"].iloc[-1]
        curr_long = df["EMA_long"].iloc[-1]

        rsi_signal = self.rsi_strategy.generate_signal(df)
        atr_signal = self.atr_strategy.generate_signal(df)

        if (
                prev_short < prev_long
                and curr_short > curr_long
                and rsi_signal == "long"
                and atr_signal == "true"
        ):
            self.short_ema_prev = curr_short
            self.long_ema_prev = curr_long
            return "long"
        elif (
                prev_short > prev_long
                and curr_short < curr_long
                and rsi_signal == "short"
                and atr_signal == "true"
        ):
            self.short_ema_prev = curr_short
            self.long_ema_prev = curr_long
            return "short"

        self.short_ema_prev = curr_short
        self.long_ema_prev = curr_long
        return "no_signal"

    def calculate_indicators(self, df):
        # Указываем индикаторы
        print("....")
        print(f"Calculate indicators for: {self.name} strategy")
        df["EMA_short"] = talib.EMA(df["close"], timeperiod=self.short_ema)
        df["EMA_long"] = talib.EMA(df["close"], timeperiod=self.long_ema)

        print("Calculating support indicators...")
        # Рассчитываем ATR
        df = self.atr_strategy.calculate_indicators(df)
        # Рассчитываем RSI
        df = self.rsi_strategy.calculate_indicators(df)

        return df
