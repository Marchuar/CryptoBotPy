from strategies.indicators import RSIIndicator, MACDIndicator, ParabolicSARIndicator, ADXIndicator, EMAIndicator, \
    ATRIndicator


class UniversalStrategy:
    def __init__(self):
        self.name = "Universal Strategy",
        self.universal_buy_treshold = 2.9
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
    def evaluate_ema(self, df, atr, close):
        ema_short = df["EMA_short"].iloc[-1] / atr
        ema_long = df["EMA_long"].iloc[-1] / atr
        ema_hist = ema_short - ema_long
        multiplier = 1.2 if abs(ema_hist) > 2.0 else 1.0

        # Разница между ценой и EMA
        ema_diff = (close - ema_short) / atr
        diff_multiplier = 1.5 if abs(ema_diff) > 1.1 else 1.0

        # Наклон EMA
        ema_slope = ema_short - ema_long
        slope_multiplier = 1.2 if abs(ema_slope) > 0.01 else 1.0

        if ema_diff > 0:
            ema_score = self.weights["EMA"] * diff_multiplier * slope_multiplier
        else:
            ema_score = -self.weights["EMA"] * diff_multiplier * slope_multiplier
        print(f"EMA short: {ema_short}, EMA long: {ema_long}, EMA hist: {ema_hist}, EMA Score: {ema_score}")
        return ema_score

    # ADX
    def evaluate_adx(self, df, score):
        adx = df["adx"].iloc[-1]
        if adx > self.adx.adx_threshold:
            score *= 1.3
        print(f"ADX: {adx}, Score after ADX: {score}")
        return score

        # RSI

    def evaluate_rsi(self, df, score):

        rsi = df["RSI"].iloc[-1]
        if 45 <= rsi <= 55:
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
        close = df["close"].iloc[-1]

        score += self.evaluate_ema(df, atr, close)
        score += self.evaluate_macd(df, atr)
        score += self.evaluate_sar(df, close)
        score = self.evaluate_adx(df, score)  # multiply
        score = self.evaluate_rsi(df, score)  # multiply

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
