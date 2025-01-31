import logging

class RSIEvaluator:
    def __init__(self):
        self.name = "RSIEvaluator"

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