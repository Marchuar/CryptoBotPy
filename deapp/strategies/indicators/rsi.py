import logging

import talib

from constants import DEFAULT_RSI_OVERBOUGHT, DEFAULT_RSI_OVERSOLD, DEFAULT_RSI_PERIOD


class RSI:
    def __init__(self,
                 rsi_overbought=DEFAULT_RSI_OVERBOUGHT,
                 rsi_oversold=DEFAULT_RSI_OVERSOLD,
                 rsi_period=DEFAULT_RSI_PERIOD):
        self.name = "RSI"
        self.candles_amount = rsi_period * 2
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        logging.info(f"Generate signal for {self.name} strategy")

        curr_rsi = df["RSI"].iloc[-1]

        if (
                curr_rsi < self.rsi_oversold
        ):
            logging.info(f"Signal for {self.name}: long")
            return "long"
        elif (
                curr_rsi > self.rsi_overbought
        ):
            logging.info(f"Signal for {self.name}: short")
            return "short"

        logging.info(f"Signal for {self.name}: no_signal")
        return "no_signal"

    def calculate_indicators(self, df):
        # Указываем индикаторы
        logging.info(f"\n....\nCalculate indicators for {self.name} strategy")
        df["RSI"] = talib.RSI(df["close"], timeperiod=self.rsi_period)
        return df
