import talib

class ADXStrategy:
    def __init__(self, adx_period=14, adx_threshold=25):
        self.name = "ADX"
        self.candles_amount = adx_period * 2
        self.adx_period = adx_period
        self.adx_threshold = adx_threshold

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        print(f"Generate signal for {self.name} strategy")

        adx = df["adx"].iloc[-1]
        curr_plus_di = df["+DI_adx"].iloc[-1]
        curr_minus_di = df["-DI_adx"].iloc[-1]
        prev_plus_di = df["+DI_adx"].iloc[-2]
        prev_minus_di = df["-DI_adx"].iloc[-2]

        # Дополнительная проверка на пересечение +DI и -DI
        # Пока не используется в проверке
        if curr_plus_di > curr_minus_di and prev_plus_di <= prev_minus_di:
            signal = "long_cross"
            print(signal)
        elif curr_minus_di > curr_plus_di and prev_minus_di <= prev_plus_di:
            signal = "short_cross"
            print(signal)

        if adx > self.adx_threshold:  # Сильный тренд
            if curr_plus_di > curr_minus_di:  # Восходящий тренд
                return "long"
            elif curr_minus_di > curr_plus_di:  # Нисходящий тренд
                return "short"  # Сигнал на продажу
            else:
                return "no_signal"
        elif adx < self.adx_threshold - 5:
            return "flat" # Боковой рынок
        else:
            return "no_signal"

    def calculate_indicators(self, df):
        # Указываем индикаторы
        print("....")
        print(f"Calculate indicators for {self.name} strategy")

        # Вычисление ADX, +DI и -DI
        df["adx"] = talib.ADX(df["high"], df["low"], df["close"], timeperiod=self.adx_period)
        df["+DI_adx"] = talib.PLUS_DI(df["high"], df["low"], df["close"], timeperiod=self.adx_period)
        df["-DI_adx"] = talib.MINUS_DI(df["high"], df["low"], df["close"], timeperiod=self.adx_period)

        return df