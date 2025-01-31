import logging

class CCIEvaluator:
    def __init__(self):
        self.name = "CCIEvaluator"

    def evaluate_cci(self, df, score, trend):
        curr_cci = df["CCI"].iloc[-1]

        if (curr_cci < 0 and curr_cci <= -100.0) or (curr_cci > 0 and curr_cci >= 100.0):
            score *= 1.1
        elif (0 < curr_cci < 40.0) or (0 > curr_cci > -40.0):
            score *= 0.8
        elif (0 < curr_cci < 80.0) or (0 > curr_cci > -80.0):
            score *= 0.9
        else:
            score *= 1.0  # Оставляем как было

        logging.info(f"Score after CCI: {score}, CCI: {curr_cci}")
        return score