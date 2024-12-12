import talib
import logging
import numpy as np

from constants import DEFAULT_BB_DEVIATION, DEFAULT_BB_PERIOD
from strategies.indicators import ATR, RSI


class BB:
    def __init__(self, bb_deviation=DEFAULT_BB_DEVIATION, bb_period=DEFAULT_BB_PERIOD):
        self.name = "BB_with_RSI_and_ATR"
        self.candles_amount = bb_period * 2
        self.bb_period = bb_period
        self.bb_deviation = bb_deviation
        self.atr_strategy = ATR()
        self.rsi_strategy = RSI()

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        logging.info(f"Generate signal for {self.name} strategy")

        curr_price = df["close"].iloc[-1]
        lower_band = df["BB_lower_band"].iloc[-1]
        upper_band = df["BB_upper_band"].iloc[-1]

        rsi_signal = self.rsi_strategy.generate_signal(df)
        atr_signal = self.atr_strategy.generate_signal(df)

        if curr_price < lower_band:
            return "long"
        elif curr_price > upper_band:
            return "short"
        else:
            return "no_signal"

        # Это надо комбинировать с RSI и ATR

    def calculate_indicators(self, df):
        # Указываем индикаторы
        logging.info(f"\n....\nCalculate indicators for {self.name} strategy")
        df["BB_upper_band"], df["BB_middle_band"], df["BB_lower_band"] = talib.BBANDS(
            np.array(df["close"]),
            timeperiod=self.bb_period,
            nbdevup=self.bb_deviation,
            nbdevdn=self.bb_deviation,
            matype=1  # BB тип: EMA
        )

        logging.info("Calculating support indicators...")
        # Рассчитываем ATR
        df = self.atr_strategy.calculate_indicators(df)
        # Рассчитываем RSI
        df = self.rsi_strategy.calculate_indicators(df)

        return df
