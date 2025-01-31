import logging

class EMAEvaluator:
    def __init__(self):
        self.name = "EMAEvaluator"

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