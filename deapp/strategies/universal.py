import logging

from strategies.indicators import RSIIndicator, MACDIndicator, ParabolicSARIndicator, ADXIndicator, EMAIndicator, \
    ATRIndicator


class UniversalStrategy:
    def __init__(self):
        self.name = "Universal Strategy",
        self.universal_buy_treshold = 2.8
        self.universal_sell_treshold = -2.84
        self.ema = EMAIndicator()
        self.rsi = RSIIndicator()
        self.macd = MACDIndicator()
        self.sar = ParabolicSARIndicator()
        self.adx = ADXIndicator()
        self.atr = ATRIndicator()
        self.candles_amount = max(self.ema.candles_amount,
                                  self.rsi.candles_amount,
                                  self.macd.candles_amount,
                                  self.sar.candles_amount,
                                  self.adx.candles_amount)
        self.weights = {
            "EMA": 0.25,
            "ADX": 0.5,
            "RSI": 1.25,
            "MACD": 1.2,
            "SAR": 0.25,
        }

    def generate_signal(self, df):
        score = self.calculate_signal_score(df)
        # df["score"] = score
        if score >= self.universal_buy_treshold:
            return "buy"
        elif score <= self.universal_sell_treshold:
            return "sell"
        return "no_signal"

    # EMA
    def evaluate_ema(self, df, atr, close, score):
        curr_ema_short = df["EMA_short"].iloc[-1] / atr
        curr_ema_long = df["EMA_long"].iloc[-1] / atr
        prev_ema_short = df["EMA_short"].iloc[-2] / atr
        prev_ema_long = df["EMA_long"].iloc[-2] / atr
        close /= atr

        # Multiplier
        ema_multiplier = 1.0

        # Test
        # score = 1

        # Растояние между EMA Short и EMA Long
        curr_ema_diff = curr_ema_long - curr_ema_short
        prev_ema_diff = prev_ema_long - prev_ema_short

        # Минимальный порог для начала анализа мультипликатора
        if close > 10000:
            ema_threshold = curr_ema_long * 0.005 # Если они на расстоянии меньше 0.5% от EMA long
            diff_factor = curr_ema_long * 0.0025 # Если изменение расстояния между ними составляет больше 0.3%
        else:
            ema_threshold = curr_ema_long * 0.01 # Если они на расстоянии меньше 1% от EMA long
            diff_factor = curr_ema_long * 0.005 # Если изменение расстояния между ними составляет больше 0.7%

        # Границы разницы EMA long и EMA short (подобрать хорошее число для границы)
        if abs(curr_ema_diff) < ema_threshold:
            # 1.Пересечение
            if curr_ema_diff * prev_ema_diff <= 0:
                ema_multiplier = 1.4
            # 2.Сужение
            elif abs(prev_ema_diff) > abs(curr_ema_diff):
                # Стремительное (надо подобрать хорошее значение)
                if abs(prev_ema_diff) - abs(curr_ema_diff) > diff_factor:
                    ema_multiplier = 1.4
                # Не стремительное
                else:
                    ema_multiplier = 1.2
            # 3. Расширение
            elif abs(curr_ema_diff) > abs(prev_ema_diff):
                # Стремительное (надо подобрать хорошее значение)
                if abs(curr_ema_diff) - abs(prev_ema_diff) > diff_factor:
                    ema_multiplier = 1.3
                # Не стремительное
                else:
                    ema_multiplier = 1.1
        # Не соответствует значению границы разницы EMA
        else:
            ema_multiplier = 1.0

        # Score after EMA
        score = score * ema_multiplier


        print(f"EMA short: {curr_ema_short}, EMA long: {curr_ema_long}, Score after EMA: {score}")
        return score

    # EMA v2
    def evaluate_macd_v2(self, df, atr):
        macd = df["macd"].iloc[-1]
        macd_prev = df["macd"].iloc[-2]
        specsignal = df["specsignal"].iloc[-1]
        specsignal_prev = df["specsignal"].iloc[-2]
        macd_hist = df["hist"].iloc[-1]
        normalized_macd_hist = macd_hist / atr

        # Пороговые значения
        macd_narrow_threshold = 0.02  # Минимальная разница для сужения
        macd_widen_threshold = 0.1  # Минимальная разница для расширения
        macd_hist_treshold = 0.15  # Порог для гистограммы
        macd_hist_border = 0.28  # Верхняя граница для гистограммы
        macd_hist_multiplier = 1.45  # Мультипликатор для гистограммы
        macd_cross = 0.01  # Порог для пересечения
        macd_cross_multiplier = 1.4  # Мультипликатор для пересечения

        macd_score = 0

        # Разница между MACD и Specsignal
        macd_diff = abs(macd - specsignal)
        macd_diff_prev = abs(macd_prev - specsignal_prev)

        # Проверка на сужение с учетом порогов и направления
        if macd_diff < macd_diff_prev and macd_diff > macd_narrow_threshold:
            print("MACD и Specsignal сужаются (в пределах допустимого диапазона)")
            if macd > specsignal:  # MACD выше сигнальной линии
                macd_score -= self.weights["MACD"] * 0.8  # Сигнал на sell
            elif macd < specsignal:  # MACD ниже сигнальной линии
                macd_score += self.weights["MACD"] * 0.8  # Сигнал на buy

        # Проверка на пересечение
        if (macd_prev < specsignal_prev and macd > specsignal) or (macd_prev > specsignal_prev and macd < specsignal):
            print("Пересечение MACD и Specsignal")
            macd_score += self.weights["MACD"] * macd_cross_multiplier * (-1 if macd < specsignal else 1)

        # Проверка на расширение с учетом порогов
        if macd_diff > macd_diff_prev and macd_diff > macd_widen_threshold:
            print("MACD и Specsignal расширяются (в пределах допустимого диапазона)")
            macd_score += self.weights["MACD"] * 1.2 * (-1 if macd < specsignal else 1)

        # Игнорируем шум (слишком частые колебания)
        if macd_diff < macd_narrow_threshold and macd_diff_prev < macd_narrow_threshold:
            print("MACD и Specsignal слишком близки, фильтруем шум")
            return 0  # Не применяем мультипликаторы

        # Дополнительная логика на основе гистограммы
        if macd > specsignal:
            if macd_hist_treshold < abs(normalized_macd_hist) <= macd_hist_border:
                macd_score += self.weights["MACD"] * macd_hist_multiplier
            else:
                macd_score += self.weights["MACD"]
        elif macd < specsignal:
            if macd_hist_treshold < abs(normalized_macd_hist) <= macd_hist_border:
                macd_score -= self.weights["MACD"] * macd_hist_multiplier
            else:
                macd_score -= self.weights["MACD"]

        print(f"MACD: {macd}, Specsignal: {specsignal}, MACD Score: {macd_score}")
        return macd_score

    # ADX
    def evaluate_adx(self, df, score):
        adx = df["adx"].iloc[-1]
        if adx > self.adx.adx_threshold:
            score *= 1.3
        print(f"ADX: {adx}, Score after ADX: {score}")
        return score

        # RSI

    def evaluate_rsi(self, df, score, adx):

        rsi = df["RSI"].iloc[-1]
        if 45 <= rsi <= 55 and adx <= 26:
            score = 0.0
            print(f">>>> RSI: {rsi}, не торгуем, плохой rsi")
            return score
        elif rsi <= 30 or rsi >= 70:
            rsi_30_70_multiplier = 1.3
            rsi_40_60_multiplier = 1.0
        elif rsi <= 40 or rsi >= 60:
            rsi_30_70_multiplier = 1.0
            rsi_40_60_multiplier = 1.15
        else:
            rsi_30_70_multiplier = 1.0
            rsi_40_60_multiplier = 1.0

        score = score * rsi_30_70_multiplier * rsi_40_60_multiplier
        print(
            f"RSI: {rsi}, RSI multiplier 30_70: {rsi_30_70_multiplier}, "
            f"RSI multiplier 40_60: {rsi_40_60_multiplier}, "
            f"Score after rsi: {score}")
        return score

    # MACD
    def evaluate_macd(self, df, atr):
        macd = df["macd"].iloc[-1]
        macd_prev = df["macd"].iloc[-2]
        specsignal = df["specsignal"].iloc[-1]
        specsignal_prev = df["specsignal"].iloc[-2]
        macd_hist = df["hist"].iloc[-1]
        normalized_macd_hist = macd_hist / atr
        macd_score = 0
        macd_hist_treshold = 0.15
        macd_hist_border = 0.28
        macd_hist_multiplier = 1.45
        macd_cross = 0.01
        macd_cross_multiplyer = 1.4

        # Усиление эффекта MACD, если гистограмма превышает порог
        # if macd_hist_treshold < abs(normalized_macd_hist) <= macd_hist_border:
        #     macd_score = self.weights["MACD"] * macd_hist_multiplier

        # Обработка пересечения MACD с нулевой линией
        if abs(normalized_macd_hist) < macd_cross:
            if macd_prev < specsignal_prev:
                macd_score = self.weights["MACD"] * macd_cross_multiplyer
            elif macd_prev > specsignal_prev:
                macd_score = -self.weights["MACD"] * macd_cross_multiplyer
        elif macd > specsignal:
            if macd_hist_treshold < abs(normalized_macd_hist) <= macd_hist_border:
                macd_score = self.weights["MACD"] * macd_hist_multiplier
            else:
                macd_score = self.weights["MACD"]
        elif macd < specsignal:
            if macd_hist_treshold < abs(normalized_macd_hist) <= macd_hist_border:
                macd_score = -self.weights["MACD"] * macd_hist_multiplier
            else:
                macd_score = -self.weights["MACD"]

        print(f"Normalized MACD Hist: {normalized_macd_hist}, Multiplier Applied: {macd_hist_multiplier}")
        print(
            f"MACD: {macd}, Specsignal: {specsignal}, Hist: {macd_hist}, Normalized Hist: {normalized_macd_hist}, MACD score: {macd_score}")
        return macd_score

    # Parabolic SAR
    def evaluate_sar(self, df, close):
        parabolic_sar = df["parabolic_sar"].iloc[-1]
        sar_score = self.weights["SAR"] if parabolic_sar < close else -self.weights["SAR"]
        print(f"Parabolic Sar: {parabolic_sar}, SAR Score: {sar_score}")
        return sar_score

    def calculate_signal_score(self, df):
        print("--------------Начало расчета скора--------------")
        print(f"Timestamp: {df['timestamp'].iloc[-1]}")

        score = 0
        atr = df["ATR"].iloc[-1]
        adx = df["adx"].iloc[-1]
        close = df["close"].iloc[-1]

        score += self.evaluate_macd(df, atr)
        score += self.evaluate_ema(df, atr, close, score) # multiply
        score += self.evaluate_sar(df, close)
        score = self.evaluate_adx(df, score)  # multiply
        score = self.evaluate_rsi(df, score, adx)  # multiply

        df.loc[df.index[-1], "score"] = score
        print(f"General score: {score}")
        print("***************Конец расчета скора***************")
        return score

    def calculate_indicators(self, df):
        df = self.ema.calculate_indicators(df)
        df = self.rsi.calculate_indicators(df)
        df = self.macd.calculate_indicators(df)
        df = self.sar.calculate_indicators(df)
        df = self.adx.calculate_indicators(df)
        df = self.atr.calculate_indicators(df)
        return df
