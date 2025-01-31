import logging

class CVDEvaluator:
    def __init__(self):
        self.name = "CVDEvaluator"

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