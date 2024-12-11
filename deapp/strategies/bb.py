import talib
import numpy as np

class BBStrategy:
    def __init__(self, bb_deviation = 2, bb_period=20):
        self.name = "BB/RSI/ATR"
        self.candles_amount = bb_period * 2
        self.bb_period = bb_period
        self.bb_deviation = bb_deviation

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        print(f"Generate signal for {self.name} strategy")

        curr_price = df["close"].iloc[-1]
        lower_band = df["BB_lower_band"].iloc[-1]
        upper_band = df["BB_upper_band"].iloc[-1]

        if curr_price < lower_band:
            return "long"
        elif curr_price > upper_band:
            return "short"
        else:
            return "no_signal"

        # Это надо комбинировать с RSI и ATR


    def calculate_indicators(self, df):
        # Указываем индикаторы
        print("....")
        print(f"Calculate indicators for {self.name} strategy")
        df["BB_upper_band"], df["BB_middle_band"], df["BB_lower_band"] = talib.BBANDS(
            np.array(df["close"]),
            timeperiod=self.bb_period,
            nbdevup=self.bb_deviation,
            nbdevdn=self.bb_deviation,
            matype=1 # BB тип: EMA
        )

        return df