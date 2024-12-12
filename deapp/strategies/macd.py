import logging
import talib

from constants import DEFAULT_FAST_PERIOD, DEFAULT_SLOW_PERIOD, DEFAULT_SIGNAL_PERIOD


class MACD:
    def __init__(self,
                 fastperiod=DEFAULT_FAST_PERIOD,
                 slowperiod=DEFAULT_SLOW_PERIOD,
                 signalperiod=DEFAULT_SIGNAL_PERIOD):
        self.name = "MACD/RSI/ATR"
        self.fastperiod = fastperiod
        self.slowperiod = slowperiod
        self.signalperiod = signalperiod
        self.candles_amount = slowperiod + signalperiod
        self.mcad_prev = 0
        self.specsignal_prev = 0

    def generate_signal(self, df):
        if len(df) < self.candles_amount:
            return "not_enough_candles"

        logging.info(f"Generate signal for {self.name} strategy")

        # Получаем последние значения для macd, signal и hist
        macd_last = df['macd'].iloc[-1]
        signal_last = df['specsignal'].iloc[-1]
        hist_last = df['hist'].iloc[-1]
        macd_prev = self.mcad_prev
        specsignal_prev = self.specsignal_prev

        if macd_prev <= specsignal_prev and macd_last > signal_last:
            self.mcad_prev = macd_last
            self.specsignal_prev = signal_last
            if hist_last > 0:
                return "long"

        if macd_prev >= specsignal_prev and macd_last < signal_last:
            self.mcad_prev = macd_last
            self.specsignal_prev = signal_last
            if hist_last < 0:
                return "short"

        self.mcad_prev = macd_last
        self.specsignal_prev = signal_last
        return "no_signal"

    def calculate_indicators(self, df):

        logging.info(f"\n....\nCalculate indicators for {self.name} strategy")
        df['macd'], df['specsignal'], df['hist'] = talib.MACD(
            df['close'],
            fastperiod=self.fastperiod,
            slowperiod=self.slowperiod,
            signalperiod=self.signalperiod
        )

        return df
