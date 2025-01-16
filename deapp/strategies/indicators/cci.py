import logging
import talib

from constants import DEFAULT_CCI_PERIOD


class CCIIndicator:
    def __init__(self, cci_period=DEFAULT_CCI_PERIOD):
        self.name = "CCI"
        self.candles_amount = cci_period
        self.cci_period = cci_period

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        logging.info(f"Generate signal for {self.name} strategy")

        curr_cci = df["CCI"].iloc[-1]

        if curr_cci < -100:
            return "long"
        elif curr_cci > 100:
            return "short"
        else:
            return "no_signal"

    def calculate_indicators(self, df):
        # Указываем индикаторы
        logging.info(f"\n....\nCalculate indicators for {self.name} strategy")
        df["CCI"] = talib.CCI(df["high"], df["low"], df["close"], timeperiod=self.cci_period)

        return df