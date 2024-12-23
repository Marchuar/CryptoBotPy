from strategies.indicators import RSIIndicator, MACDIndicator, ParabolicSARIndicator, ADXIndicator, EMAIndicator


class UniversalStrategy:
    def __init__(self):
        self.name = "Universal Strategy",
        self.universal_buy_treshold = 3.5
        self.universal_sell_treshold = -2.5
        self.ema = EMAIndicator()
        self.rsi = RSIIndicator()
        self.macd = MACDIndicator()
        self.sar = ParabolicSARIndicator()
        self.adx = ADXIndicator()
        self.candles_amount = max(self.ema.candles_amount,
                                  self.rsi.candles_amount,
                                  self.macd.candles_amount,
                                  self.sar.candles_amount,
                                  self.adx.candles_amount)

    def generate_signal(self, df):
        score = self.calculate_signal_score(df)
        df["score"] = score
        if score >= self.universal_buy_treshold:
            return "buy"
        elif score <= self.universal_sell_treshold:
            return "sell"
        return "no_signal"

    def calculate_signal_score(self, df):
        score = 0
        weights = self.calculate_indicators_weights()

        # EMA
        ema_hist = df["EMA_short"].iloc[-1] - df["EMA_long"].iloc[-1]
        if ema_hist > 2 or ema_hist < -2:
            ema_hist_multiplier = 1.2
        else:
            ema_hist_multiplier = 1.0
        if df["EMA_short"].iloc[-1] > df["EMA_long"].iloc[-1]:
            score += weights["EMA"] * ema_hist_multiplier
        else:
            score -= weights["EMA"] * ema_hist_multiplier

        # ADX
        adx_multiplier = 1.2
        if df["adx"].iloc[-1] > self.adx.adx_threshold:
            score *= adx_multiplier

        # RSI
        if 30 <= df["RSI"].iloc[-1] <= 70:
            score = score + (weights["RSI"] * 0.5)
        else:
            score += weights["RSI"]

        # MACD
        if df["macd"].iloc[-1] > df["specsignal"].iloc[-1]:
            score += weights["MACD"]
        else:
            score -= weights["MACD"]
        macd_hist_multiplier = 1.45
        if df["hist"].iloc[-1] > 0.48 or df["hist"].iloc[-1] < -0.48:
            score *= macd_hist_multiplier

        # Parabolic SAR
        if df["parabolic_sar"].iloc[-1] < df["close"].iloc[-1]:
            score += weights["SAR"]
        else:
            score -= weights["SAR"]

        df.loc[df.index[-1], "score"] = score
        return score

    def calculate_indicators(self, df):
        df = self.ema.calculate_indicators(df)
        df = self.rsi.calculate_indicators(df)
        df = self.macd.calculate_indicators(df)
        df = self.sar.calculate_indicators(df)
        df = self.adx.calculate_indicators(df)
        return df

    def calculate_indicators_weights(self):
        # Сюда можно будет добавить логику в зависимости от рынка менять веса
        weights = {
            "EMA": 0.75,
            "ADX": 2.0,
            "RSI": 1.0,
            "MACD": 2.5,
            "SAR": 0.75,
        }
        return weights
