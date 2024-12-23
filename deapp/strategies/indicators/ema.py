import logging
import talib

from constants import DEFAULT_SHORT_EMA, DEFAULT_LONG_EMA


class EMAIndicator:
    def __init__(self, short_ema=DEFAULT_SHORT_EMA, long_ema=DEFAULT_LONG_EMA):
        self.name = "EMA"
        self.candles_amount = max(short_ema, long_ema)
        self.short_ema = short_ema
        self.long_ema = long_ema

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        logging.info(f"Generate signal for {self.name} strategy")

        curr_short = df["EMA_short"].iloc[-1]
        curr_long = df["EMA_long"].iloc[-1]

        if curr_short > curr_long:
            return "long"
        elif curr_short < curr_long:
            return "short"
        else:
            return "no_signal"

    def calculate_indicators(self, df):
        # Указываем индикаторы
        logging.info(f"\n....\nCalculate indicators for {self.name} strategy")
        df["EMA_short"] = talib.EMA(df["close"], timeperiod=self.short_ema)
        df["EMA_long"] = talib.EMA(df["close"], timeperiod=self.long_ema)

        return df