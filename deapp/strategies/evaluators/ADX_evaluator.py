import logging

class ADXEvaluator:
    def __init__(self, adx):
        self.name = "ADXEvaluator"
        self.adx = adx

    # ADX - сомнительно надо ли вообще вот это
    def evaluate_adx(self, df, score):
        adx = df["adx"].iloc[-1]
        adx_multiplier = 1.2

        if adx > self.adx.adx_threshold:
            score *= adx_multiplier
        logging.info(f"Score after ADX: {score}, ADX: {adx}")
        return score