import talib


class MACDStrategy:
    def __init__(self, fastperiod=12, slowperiod=26, signalperiod=9):
        self.name = "MACD"
        self.fastperiod = fastperiod
        self.slowperiod = slowperiod
        self.signalperiod = signalperiod
        self.candles_amount = slowperiod + signalperiod
        self.mcad_prev = 0
        self.specsignal_prev = 0

    def generate_signal(self, df):
        if len(df) < self.candles_amount:
            return "not_enough_candles"

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

        df['macd'], df['specsignal'], df['hist'] = talib.MACD(
            df['close'],
            fastperiod=self.fastperiod,
            slowperiod=self.slowperiod,
            signalperiod=self.signalperiod
        )

        return df
