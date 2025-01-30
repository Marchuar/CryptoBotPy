import logging

from strategies.indicators import RSIIndicator, MACDIndicator, ParabolicSARIndicator, ADXIndicator, EMAIndicator, \
    ATRIndicator, CVDIndicator
from strategies.indicators.cci import CCIIndicator

from strategies.evaluators.MACDEvaluator import MACDEvaluator

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
        self.candles_amount = max(self.ema.candles_amount,
                                  self.rsi.candles_amount,
                                  self.macd.candles_amount,
                                  self.sar.candles_amount,
                                  self.adx.candles_amount,
                                  self.cci.candles_amount)

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
        recent_prices = df["close"].iloc[-10:]  # Последние цены закрытия 20 свечей

        # Смотрим какой тренд, на покупку или продажу
        trend = self.determine_trend(macd_hist, macd_hist_prev, rsi, adx, cci, recent_prices)

        if trend == "no_signal":
            return "no_signal"

        score = self.calculate_signal_score(df, trend, atr, close, close_prev)

        if score >= self.universal_buy_treshold:
            return "buy"
        elif score <= self.universal_sell_treshold:
            return "sell"
        return "no_signal"

    # EMA
    def evaluate_ema(self, df, atr, close, score):
        curr_ema_short = df["EMA_short"].iloc[-1]
        curr_ema_long = df["EMA_long"].iloc[-1]
        prev_ema_short = df["EMA_short"].iloc[-2]
        prev_ema_long = df["EMA_long"].iloc[-2]

        # Multiplier
        ema_multiplier = 1.0

        # Test
        # score = 1

        # Растояние между EMA Short и EMA Long
        curr_ema_diff = curr_ema_long - curr_ema_short
        prev_ema_diff = prev_ema_long - prev_ema_short

        # Минимальный порог для начала анализа мультипликатора
        if close > 10000:
            ema_threshold = curr_ema_long * 0.05  # Если они на расстоянии меньше 0.5% от EMA long
            diff_factor = curr_ema_long * 0.0025  # Если изменение расстояния между ними составляет больше 0.3%
        else:
            ema_threshold = curr_ema_long * 0.1  # Если они на расстоянии меньше 1% от EMA long
            diff_factor = curr_ema_long * 0.005  # Если изменение расстояния между ними составляет больше 0.5%

        # Границы разницы EMA long и EMA short (подобрать хорошее число для границы)
        if abs(curr_ema_diff) < ema_threshold:
            # 1.Пересечение
            if curr_ema_diff * prev_ema_diff <= 0:
                ema_multiplier = 1.4
                logging.info("EMA: Crossing EMA")
            # 2.Сужение
            elif abs(prev_ema_diff) > abs(curr_ema_diff):
                # Стремительное (надо подобрать хорошее значение)
                if abs(prev_ema_diff) - abs(curr_ema_diff) > diff_factor:
                    ema_multiplier = 1.4
                    logging.info("EMA: Стремительное сужение")
                # Не стремительное
                else:
                    ema_multiplier = 1.2
                    logging.info("EMA: Обычное сужение")
            # 3. Расширение
            elif abs(curr_ema_diff) > abs(prev_ema_diff):
                # Стремительное (надо подобрать хорошее значение)
                if abs(curr_ema_diff) - abs(prev_ema_diff) > diff_factor:
                    ema_multiplier = 1.3
                    logging.info("EMA: Стремительное расширение")
                # Не стремительное
                else:
                    ema_multiplier = 1.1
                    logging.info("EMA: Обычное расширение")
        # Не соответствует значению границы разницы EMA
        else:
            ema_multiplier = 1.0
            logging.info("EMA: Не входит в границы")

        # Score after EMA
        score = score * ema_multiplier

        logging.info(f"EMA short: {curr_ema_short}, EMA long: {curr_ema_long}, Score after EMA: {score}")
        return score

    # ADX - сомнительно надо ли вообще вот это
    def evaluate_adx(self, df, score):
        adx = df["adx"].iloc[-1]
        adx_multiplier = 1.2

        if adx > self.adx.adx_threshold:
            score *= adx_multiplier
        logging.info(f"Score after ADX: {score}, ADX: {adx}")
        return score

    def evaluate_cvd(self, df, close, close_prev):
        cvd = df["CVD"].iloc[-1]
        cvd_prev = df["CVD"].iloc[-2]

        # Проверка на дивергенции
        if close > close_prev and cvd < cvd_prev:
            logging.info("Short: проверка CVD")
        elif close < close_prev and cvd > cvd_prev:
            logging.info("Long: проверка CVD")
        else:
            logging.info("Nothing: проверка CVD")

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
            rsi_40_60_multiplier = 0.9

        score = score * rsi_30_70_multiplier * rsi_40_60_multiplier
        logging.info(
            f"Score after rsi: {score}, "
            f"RSI: {rsi}, RSI multiplier 30_70: {rsi_30_70_multiplier}, "
            f"RSI multiplier 40_60: {rsi_40_60_multiplier}")
        return score

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

        logging.info(f"Score after SAR: {score}, Parabolic Sar: {parabolic_sar}")
        return score

    def evaluate_cci(self, df, score, trend):
        curr_cci = df["CCI"].iloc[-1]

        if (curr_cci < 0 and curr_cci <= -100.0) or (curr_cci > 0 and curr_cci >= 100.0):
            score *= 1.1
        elif (0 < curr_cci < 40.0) or (0 > curr_cci > -40.0):
            score *= 0.8
        elif (0 < curr_cci < 80.0) or (0 > curr_cci > -80.0):
            score *= 0.9
        else:
            score *= 1.0 # Оставляем как было

        logging.info(f"Score after CCI: {score}, CCI: {curr_cci}")
        return score

    def calculate_signal_score(self, df, trend, atr, close, close_prev):
        logging.info("--------------Calculating the score--------------")
        logging.info(f"Timestamp: {df['timestamp'].iloc[-1]}")

        score = self.basic_score(trend)

        score = self.evaluate_ema(df, atr, close, score)
        score = self.evaluate_sar(df, close, trend, score)
        score = self.evaluate_adx(df, score)
        score = self.evaluate_rsi(df, score)
        score = self.MACDEvaluator.evaluate_macd(df, score, trend, atr)
        # self.evaluate_cvd(df, close, close_prev) / не работает, пересмотреть логику
        score = self.evaluate_cci(df, score, trend)

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
