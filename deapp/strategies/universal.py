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

    def determine_trend(self, macd, macd_prev, rsi, adx):

        if 45 <= rsi <= 55 and adx <= 26:
            print(f">>>> RSI: {rsi}, ADX: {adx} - не торгуем")
            return "no_signal"
        else:
            if macd > macd_prev:
                return "buy"
            elif macd < macd_prev:
                return "sell"
            return "no_signal"

    def basic_score(self, trend):
        score = 1
        if trend == "sell":
            score = -score

        print(f"Расчитан базовый скор: {score}")
        return score

    def generate_signal(self, df):

        macd = df["macd"].iloc[-1]
        macd_prev = df["macd"].iloc[-2]
        rsi = df["RSI"].iloc[-1]
        adx = df["adx"].iloc[-1]
        atr = df["ATR"].iloc[-1]
        close = df["close"].iloc[-1]

        # Смотрим какой тренд, на покупку или продажу
        trend = self.determine_trend(macd, macd_prev, rsi, adx)

        if trend == "no_signal":
            return "no_signal"

        score = self.calculate_signal_score(df, trend, atr, close)

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

    # MACD v2
    def evaluate_macd(self, df, score, trend, atr):

        macd = df["macd"].iloc[-1]
        macd_prev = df["macd"].iloc[-2]
        specsignal = df["specsignal"].iloc[-1]
        specsignal_prev = df["specsignal"].iloc[-2]
        macd_hist = df["hist"].iloc[-1]
        macd_hist_prev = df["hist"].iloc[-2]
        normalized_macd_hist = macd_hist / atr
        normalized_macd_hist_prev = macd_hist_prev / atr

        # Tresholds
        macd_narrow_threshold = 0.065  # Минимальная разница для сужения
        macd_extension_threshold = 0.065  # Минимальная разница для расширения

        # Multiplicators
        macd_extension_multiplier = 1.2
        macd_cross_multiplier = 1.4
        macd_narrow_multiplier = 1.5

        # Логика пересечения
        if normalized_macd_hist * normalized_macd_hist_prev <= 0:
            print("Пересечение MACD и Specsignal")
            score *= macd_cross_multiplier
        # Логика сужения
        elif abs(normalized_macd_hist) < macd_narrow_threshold < abs(normalized_macd_hist_prev) and abs(
                normalized_macd_hist) < abs(normalized_macd_hist_prev):
            print("MACD и Specsignal сужаются в пределах диапозона")
            score *= macd_narrow_multiplier
        # Логика расширения
        elif abs(normalized_macd_hist) > macd_extension_threshold > abs(normalized_macd_hist_prev) and abs(
                normalized_macd_hist) > abs(normalized_macd_hist_prev):
            print("MACD и Specsignal расширяются в пределах диапозона")
            score *= macd_extension_multiplier

        print(f"Score after MACD: {score}, "
              f"MACD: {macd}, Specsignal: {specsignal}, MACD hist: {normalized_macd_hist}, MACD prev hist: {normalized_macd_hist_prev}, "
              f"Trend: {trend}")
        return score

    # ADX - сомнительно надо ли вообще вот это
    def evaluate_adx(self, df, score):
        adx = df["adx"].iloc[-1]
        adx_multiplier = 1.2

        if adx > self.adx.adx_threshold:
            score *= adx_multiplier
        print(f"Score after ADX: {score}, ADX: {adx}")
        return score

    # RSI
    def evaluate_rsi(self, df, score):

        rsi = df["RSI"].iloc[-1]

        if rsi <= 30 or rsi >= 70:
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
            f"Score after rsi: {score}, "
            f"RSI: {rsi}, RSI multiplier 30_70: {rsi_30_70_multiplier}, "
            f"RSI multiplier 40_60: {rsi_40_60_multiplier}")
        return score

    # # MACD
    # def evaluate_macd(self, df, atr):
    #     macd = df["macd"].iloc[-1]
    #     macd_prev = df["macd"].iloc[-2]
    #     specsignal = df["specsignal"].iloc[-1]
    #     specsignal_prev = df["specsignal"].iloc[-2]
    #     macd_hist = df["hist"].iloc[-1]
    #     normalized_macd_hist = macd_hist / atr
    #     macd_score = 0
    #     macd_hist_treshold = 0.15
    #     macd_hist_border = 0.28
    #     macd_hist_multiplier = 1.45
    #     macd_cross = 0.01
    #     macd_cross_multiplyer = 1.4
    #
    #     # Усиление эффекта MACD, если гистограмма превышает порог
    #     # if macd_hist_treshold < abs(normalized_macd_hist) <= macd_hist_border:
    #     #     macd_score = self.weights["MACD"] * macd_hist_multiplier
    #
    #     # Обработка пересечения MACD с нулевой линией
    #     if abs(normalized_macd_hist) < macd_cross:
    #         if macd_prev < specsignal_prev:
    #             macd_score = self.weights["MACD"] * macd_cross_multiplyer
    #         elif macd_prev > specsignal_prev:
    #             macd_score = -self.weights["MACD"] * macd_cross_multiplyer
    #     elif macd > specsignal:
    #         if macd_hist_treshold < abs(normalized_macd_hist) <= macd_hist_border:
    #             macd_score = self.weights["MACD"] * macd_hist_multiplier
    #         else:
    #             macd_score = self.weights["MACD"]
    #     elif macd < specsignal:
    #         if macd_hist_treshold < abs(normalized_macd_hist) <= macd_hist_border:
    #             macd_score = -self.weights["MACD"] * macd_hist_multiplier
    #         else:
    #             macd_score = -self.weights["MACD"]
    #
    #     print(f"Normalized MACD Hist: {normalized_macd_hist}, Multiplier Applied: {macd_hist_multiplier}")
    #     print(
    #         f"MACD: {macd}, Specsignal: {specsignal}, Hist: {macd_hist}, Normalized Hist: {normalized_macd_hist}, MACD score: {macd_score}")
    #     return macd_score

    # Parabolic SAR
    def evaluate_sar(self, df, close, trend, score):
        parabolic_sar = df["parabolic_sar"].iloc[-1]

        # Мультипликаторы
        sar_multiplier_positive = 1.2  # Усиление тренда
        sar_multiplier_negative = 1.0  # Ослабление тренда

        # Корректировка счета в зависимости от тренда и SAR
        if trend == "buy":
            if close > parabolic_sar:
                # Подтверждение тренда на покупку
                score *= sar_multiplier_positive
            elif close < parabolic_sar:
                # Возможный разворот
                score *= sar_multiplier_negative
        elif trend == "sell":
            if close < parabolic_sar:
                # Подтверждение тренда на продажу
                score *= sar_multiplier_positive
            elif close > parabolic_sar:
                # Возможный разворот
                score *= sar_multiplier_negative

        print(f"Score after SAR: {score}, Parabolic Sar: {parabolic_sar}")
        return score

    def calculate_signal_score(self, df, trend, atr, close):
        print("--------------Начало расчета скора--------------")
        print(f"Timestamp: {df['timestamp'].iloc[-1]}")

        score = self.basic_score(trend)

        score = self.evaluate_ema(df, atr, close, score)
        score = self.evaluate_sar(df, close, trend, score)
        score = self.evaluate_adx(df, score)
        score = self.evaluate_rsi(df, score)
        score = self.evaluate_macd(df, score, trend, atr)

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
