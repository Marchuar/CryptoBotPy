import talib

class EMAStrategy:
    def __init__(self, short_ema = 50, long_ema = 100):
        self.short_ema = short_ema
        self.long_ema = long_ema

    def generate_signal(self, df):

        df = df.copy()

        print(df)
        # Указываем индикаторы
        df["EMA_short"] = talib.EMA(df["close"], timeperiod=self.short_ema)
        df["EMA_long"] = talib.EMA(df["close"], timeperiod=self.long_ema)

        # Чекаем достаточно ли данных для сигнала
        if len(df) < self.long_ema:
            print("Недостаточно данных")
            return None  # Недостаточно данных

        prev_short = df["EMA_short"].iloc[-2]
        prev_long = df["EMA_long"].iloc[-2]
        curr_short = df["EMA_short"].iloc[-1]
        curr_long = df["EMA_long"].iloc[-1]

        print("EMA_short_prev[-2]: " + str(prev_short))
        print("EMA_long_prev[-2]: " + str(prev_long))
        print("EMA_short[-1]: " + str(curr_short))
        print("EMA_long[-1]: " + str(curr_long))

        if prev_short < prev_long and curr_short > curr_long:
            return "long"
        elif prev_short > prev_long and curr_short < curr_long:
            return "short"
        return None