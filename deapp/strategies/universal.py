import logging
from strategies.indicators import RSIIndicator, MACDIndicator, ParabolicSARIndicator, ADXIndicator, EMAIndicator


class UniversalStrategy:
    def __init__(self):
        self.name = "Universal Strategy",
        self.ema = EMAIndicator()
        self.rsi = RSIIndicator()
        self.macd = MACDIndicator()
        self.sar = ParabolicSARIndicator()
        self.adx = ADXIndicator()
        self.candles_amount = max(self.ema.candles_amount,
                                  self.rsi.candles_amount,
                                  self.macd.candles_amount,
                                  self.sar.candles_amount,
                                  self.adx.candles_amount)

    def generate_signal(self, df):
        if (
                df["EMA_short"].iloc[-1] > df["EMA_long"].iloc[-1] and  # EMA тренд вверх
                df["adx"].iloc[-1] > 25 and  # Сильный тренд
                30 <= df["RSI"].iloc[-1] <= 70 and  # RSI нейтральная зона
                df["macd"].iloc[-1] > df["specsignal"].iloc[-1] and  # MACD пересечение вверх
                df["parabolic_sar"].iloc[-1] < df["close"].iloc[-1]  # SAR ниже цены
        ):
            return "buy"
            # Условия для продажи
        elif (
                df["EMA_short"].iloc[-1] < df["EMA_long"].iloc[-1] and  # EMA тренд вниз
                df["adx"].iloc[-1] > 25 and  # Сильный тренд
                30 <= df["RSI"].iloc[-1] <= 70 and  # RSI нейтральная зона
                df["macd"].iloc[-1] < df["specsignal"].iloc[-1] and  # MACD пересечение вниз
                df["parabolic_sar"].iloc[-1] > df["close"].iloc[-1]  # SAR выше цены
        ):
            return "sell"
        return "no_signal"

    def calculate_indicators(self, df):
        df = self.ema.calculate_indicators(df)
        df = self.rsi.calculate_indicators(df)
        df = self.macd.calculate_indicators(df)
        df = self.sar.calculate_indicators(df)
        df = self.adx.calculate_indicators(df)
        return df
