import logging

class SAREvaluator:
    def __init__(self):
        self.name = "SAREvaluator"

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