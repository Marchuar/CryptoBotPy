import logging

from strategies.indicators import RSIIndicator, MACDIndicator, ParabolicSARIndicator, ADXIndicator, EMAIndicator, \
    ATRIndicator, CVDIndicator
from strategies.indicators.cci import CCIIndicator

from strategies.evaluators import MACDEvaluator, EMAEvaluator, SAREvaluator, ADXEvaluator, RSIEvaluator, \
    CVDEvaluator, CCIEvaluator


class UniversalStrategy:
    def __init__(self):
        self.name = "Universal Strategy",
        self.universal_buy_treshold = 3.1
        self.universal_sell_treshold = -3.1
        self.ema = EMAIndicator()
        self.rsi = RSIIndicator()
        self.macd = MACDIndicator()
        self.sar = ParabolicSARIndicator()
        self.adx = ADXIndicator()
        self.atr = ATRIndicator()
        self.cci = CCIIndicator()
        self.cvd = CVDIndicator()
        self.MACDEvaluator = MACDEvaluator()
        self.EMAEvaluator = EMAEvaluator()
        self.SAREvaluator = SAREvaluator()
        self.ADXEvaluator = ADXEvaluator(self.adx)
        self.RSIEvaluator = RSIEvaluator()
        self.CVDEvaluator = CVDEvaluator()
        self.CCIEvaluator = CCIEvaluator()
        self.candles_amount = max(self.ema.candles_amount,
                                  self.rsi.candles_amount,
                                  self.macd.candles_amount,
                                  self.sar.candles_amount,
                                  self.adx.candles_amount,
                                  self.cci.candles_amount) + 10

    def determine_trend(self, macd_hist, macd_hist_prev, rsi, adx, cci, recent_prices):

        # Расчет диапазона цен для определения бокового движения
        max_price = recent_prices.max()
        min_price = recent_prices.min()
        avg_price = (max_price + min_price) / 2
        price_range = max_price - min_price
        percent_range = (price_range / avg_price) * 100

        range_threshold = 5.0  # Процентный порог для бокового движения

        # if percent_range <= range_threshold:
        #     print(
        #         f">>>> Диапазон цен {price_range} ({percent_range:.2f}%) меньше {range_threshold}%. Боковое движение.")
        #     return "no_signal"

        if 0 <= cci <= 15 or 0 >= cci >= -15:
            logging.info(f">>>> CCI: {cci} - not trading")
            return "no_signal"

        if 43 <= rsi <= 57 and adx <= 27:
            logging.info(f">>>> RSI: {rsi}, ADX: {adx} - not trading")
            return "no_signal"
        else:
            if macd_hist > macd_hist_prev:
                return "buy"
            elif macd_hist < macd_hist_prev:
                return "sell"
            return "no_signal"

    def basic_score(self, trend):
        score = 1
        if trend == "sell":
            score = -score

        logging.info(f"Calculated base score: {score}")
        return score

    def generate_signal(self, df):

        macd = df["macd"].iloc[-1]
        macd_prev = df["macd"].iloc[-2]
        macd_hist = df["hist"].iloc[-1]
        macd_hist_prev = df["hist"].iloc[-2]
        rsi = df["RSI"].iloc[-1]
        adx = df["adx"].iloc[-1]
        atr = df["ATR"].iloc[-1]
        cci = df["CCI"].iloc[-1]
        close = df["close"].iloc[-1]
        close_prev = df["close"].iloc[-2]
        recent_prices = df["close"].iloc[-10:]  # Последние цены закрытия 10 свечей

        # Смотрим какой тренд, на покупку или продажу
        trend = self.determine_trend(macd_hist, macd_hist_prev, rsi, adx, cci, recent_prices)

        if trend == "no_signal":
            return "no_signal"

        score = self.calculate_signal_score(df, trend, atr, close, close_prev)

        if score >= self.universal_buy_treshold:
            return "buy", score
        elif score <= self.universal_sell_treshold:
            return "sell", score
        return "no_signal"


    def calculate_signal_score(self, df, trend, atr, close, close_prev):
        logging.info("--------------Calculating the score--------------")
        logging.info(f"Timestamp: {df['timestamp'].iloc[-1]}")

        score = self.basic_score(trend)

        score = self.EMAEvaluator.evaluate_ema(df, atr, close, score)
        score = self.SAREvaluator.evaluate_sar(df, close, trend, score)
        score = self.ADXEvaluator.evaluate_adx(df, score)
        score = self.RSIEvaluator.evaluate_rsi(df, score)
        score = self.MACDEvaluator.evaluate_macd(df, score, trend, atr)
        # self.CVDEvaluator.evaluate_cvd(df, close, close_prev) / не работает, пересмотреть логику
        score = self.CCIEvaluator.evaluate_cci(df, score, trend)

        df.loc[df.index[-1], "score"] = score
        logging.info(f"General score: {score}")
        logging.info("***************The end of the score calculation***************")
        return score

    def calculate_indicators(self, df):
        df = self.ema.calculate_indicators(df)
        df = self.rsi.calculate_indicators(df)
        df = self.macd.calculate_indicators(df)
        df = self.sar.calculate_indicators(df)
        df = self.adx.calculate_indicators(df)
        df = self.atr.calculate_indicators(df)
        df = self.cvd.calculate_indicators(df)
        df = self.cci.calculate_indicators(df)
        return df
