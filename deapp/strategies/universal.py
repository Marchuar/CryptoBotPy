from strategies.indicators import RSIIndicator, MACDIndicator, ParabolicSARIndicator, ADXIndicator, EMAIndicator, \
    ATRIndicator


class UniversalStrategy:
    def __init__(self):
        self.name = "Universal Strategy",
        self.universal_buy_treshold = 2.9
        self.universal_sell_treshold = -2.5
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
            "EMA": 0.75,
            "ADX": 0.5,
            "RSI": 1.25,
            "MACD": 1.75,
            "SAR": 0.75,
        }

    def generate_signal(self, df):
        score = self.calculate_signal_score(df)
        df["score"] = score
        if score >= self.universal_buy_treshold:
            return "buy"
        elif score <= self.universal_sell_treshold:
            return "sell"
        return "no_signal"

    # EMA
    def evaluate_ema(self, df, atr):
        ema_short = df["EMA_short"].iloc[-1] / atr
        ema_long = df["EMA_long"].iloc[-1] / atr
        ema_hist = ema_short - ema_long
        multiplier = 1.2 if abs(ema_hist) > 2.0 else 1.0

        if ema_short > ema_long:
            ema_score = self.weights["EMA"] * multiplier
        else:
            ema_score = -self.weights["EMA"] * multiplier
        print(f"EMA Score: {ema_score}")
        return ema_score

    # ADX
    def evaluate_adx(self, df):
        adx = df["adx"].iloc[-1]
        adx_score = 0
        if adx > self.adx.adx_threshold:
            adx_score = self.weights["ADX"] * 1.75
        print(f"ADX score: {adx_score}")
        return adx_score

        # RSI

    def evaluate_rsi(self, df):
        rsi = df["RSI"].iloc[-1]
        rsi_multiplier = 0.5 if 30 <= rsi <= 70 else 1.0
        rsi_score = self.weights["RSI"] * rsi_multiplier
        print(f"RSI Score: {rsi_score}")
        return rsi_score

    # MACD
    def evaluate_macd(self, df, atr):
        macd = df["macd"].iloc[-1]
        specsignal = df["specsignal"].iloc[-1]
        macd_hist = df["hist"].iloc[-1]
        normalized_macd_hist = macd_hist / atr
        macd_score = 0
        macd_hist_treshold = 0.43
        macd_hist_multiplier = 1.45
        macd_cross = 0.01
        macd_cross_multiplyer = 1.6

        # Усиление эффекта MACD, если гистограмма превышает порог
        if abs(normalized_macd_hist) > macd_hist_treshold:
            macd_score = self.weights["MACD"] * macd_hist_multiplier
            print(f"Normalized MACD Hist: {normalized_macd_hist}, Multiplier Applied: {macd_hist_multiplier}")

        # Обработка пересечения MACD с нулевой линией
        if -macd_cross < normalized_macd_hist < macd_cross:
            macd_score = self.weights["MACD"] * macd_cross_multiplyer
        else:
            if macd > specsignal:
                macd_score += self.weights["MACD"]
            else:
                macd_score -= self.weights["MACD"]

        print(f"MACD: {macd}, Specsignal: {specsignal}, Hist: {macd_hist}, Normalized Hist: {normalized_macd_hist}")
        print(f"MACD score: {macd_score}")
        return macd_score

    # Parabolic SAR
    def evaluate_sar(self, df, close):
        parabolic_sar = df["parabolic_sar"].iloc[-1]
        sar_score = self.weights["SAR"] if parabolic_sar < close else -self.weights["SAR"]
        print(f"SAR Score: {sar_score}")
        return sar_score

    def calculate_signal_score(self, df):
        print("--------------Начало расчета скора--------------")
        print(f"Timestamp: {df['timestamp'].iloc[-1]}")

        score = 0
        atr = df["ATR"].iloc[-1]
        close = df["close"].iloc[-1]

        score += self.evaluate_ema(df, atr)
        score += self.evaluate_adx(df)
        score += self.evaluate_rsi(df)
        score += self.evaluate_macd(df, atr)
        score += self.evaluate_sar(df, close)

        df.loc[df.index[-1], "score"] = score
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
