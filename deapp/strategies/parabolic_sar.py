import talib

class ParabolicSARStrategy:
    def __init__(self, sar_acceleration=0.02, sar_maximum=0.2):
        self.name = "ParabolicSAR"
        self.candles_amount = 30
        self.sar_acceleration = sar_acceleration
        self.sar_maximum = sar_maximum

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        print(f"Generate signal for {self.name} strategy")

        parabolic_sar = df["parabolic_sar"].iloc[-1]
        curr_price = df["close"].iloc[-1]

        if curr_price > parabolic_sar:
            return "long"
        elif curr_price < parabolic_sar:
            return "short"
        else:
            return "no_signal"

    def calculate_indicators(self, df):
        # Указываем индикаторы
        print("....")
        print(f"Calculate indicators for {self.name} strategy")

        # Вычисление Parabolic SAR
        df["parabolic_sar"] = talib.SAR(
            df["high"],
            df["low"],
            acceleration=self.sar_acceleration,
            maximum=self.sar_maximum
        )

        return df