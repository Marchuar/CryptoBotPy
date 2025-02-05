import logging
import numpy as np


class MACDEvaluator:
    def __init__(self):
        self.name = "MACDEvaluator"

    # MACD v2
    def evaluate_macd(self, df, score, trend, atr):

        macd = df["macd"].iloc[-1]
        macd_prev = df["macd"].iloc[-2]
        specsignal = df["specsignal"].iloc[-1]
        specsignal_prev = df["specsignal"].iloc[-2]
        macd_hist = df["hist"].iloc[-1]
        macd_hist_prev = df["hist"].iloc[-2]
        normalized_macd_hist = macd_hist / atr
        normalized_macd_hist_prev = macd_hist_prev / atr

        # Рассчитываем динамический threshold
        macd_line = df["macd"].iloc[-15:]  # Используем последние 15 значений для анализа
        signal_line = df["specsignal"].iloc[-15:]
        macd_hist_15 = df["hist"].iloc[-15:] # Берём последние 15 значений MACD_hist
        # Очищаем индексы
        macd_line = macd_line.reset_index(drop=True)
        signal_line = signal_line.reset_index(drop=True)
        macd_hist_15 = macd_hist_15.reset_index(drop=True)
        # Считаем threshold
        dynamic_threshold = self.calculate_threshold(macd_hist_15)

        # Проверяем боковой рынок
        is_sideways_market = self.is_sideways_market(macd_hist_15, dynamic_threshold)
        if is_sideways_market:
            logging.info("Рынок в боковике. Снижаем приоритет MACD.")
            score *= 0.8  # Снижаем score для бокового рынка
            return score

        # Tresholds
        macd_narrow_threshold = 0.065  # Минимальная разница для сужения
        macd_extension_threshold = 0.065  # Минимальная разница для расширения
        strong_movement_threshold = 100  # Порог для сильного изменения (%)

        # Multiplicators
        macd_extension_multiplier = 1.0 # Расширение пока пусть будет, но с множителем 1
        macd_cross_multiplier = 1.8
        macd_narrow_multiplier = 1.7
        strong_movement_multiplier = 1.8  # Дополнительный множитель для сильных изменений

        # Относительное изменение hist
        hist_change = abs(normalized_macd_hist - normalized_macd_hist_prev) / abs(normalized_macd_hist_prev) * 100

        # Логика пересечения
        if normalized_macd_hist * normalized_macd_hist_prev <= 0:
            # Логика сильного изменения
            if hist_change >= strong_movement_threshold:
                logging.info("Сильное изменение гистограммы MACD")
                score *= strong_movement_multiplier

            logging.info("Пересечение MACD и Specsignal")
            score *= macd_cross_multiplier
        # Логика сужения
        elif abs(normalized_macd_hist) < macd_narrow_threshold < abs(normalized_macd_hist_prev) and abs(
                normalized_macd_hist) < abs(normalized_macd_hist_prev):
            # Логика сильного изменения
            if hist_change >= strong_movement_threshold:
                logging.info("Сильное изменение гистограммы MACD")
                score *= strong_movement_multiplier

            logging.info("MACD и Specsignal сужаются в пределах диапозона")
            score *= macd_narrow_multiplier
        # Логика расширения (возможно надо вообще убрать)
        elif abs(normalized_macd_hist) > macd_extension_threshold > abs(normalized_macd_hist_prev) and abs(
                normalized_macd_hist) > abs(normalized_macd_hist_prev):
            logging.info("MACD и Specsignal расширяются в пределах диапозона")
            score *= macd_extension_multiplier

        logging.info(f"Score after MACD: {score}, "
                f"MACD: {macd}, Specsignal: {specsignal}, "
                f"MACD hist: {normalized_macd_hist}, MACD prev hist: {normalized_macd_hist_prev}, "
                f"Hist change: {hist_change}%"
                f"Trend: {trend}")
        return score

    @staticmethod
    def calculate_threshold(macd_hist_15):
        # Рассчитывает порог на основе стандартного отклонения MACD.

        threshold = sum(map(abs, macd_hist_15)) / len(macd_hist_15) * 0.2
        logging.info(f"Threshold: {threshold}")
        return threshold

    @staticmethod
    def is_sideways_market(macd_hist_15, threshold, min_crosses=3):

        # Проверяет наличие бокового рынка на основе MACD.
        is_macd_flat = True
        score = 0 # score для выхода разницы macd_hist за пределы threshold
        for i in range(0, len(macd_hist_15) - 6):
            if abs(macd_hist_15[i] - macd_hist_15[i + 1]) >= threshold:
                score = score + 1
        # Надо набрать 4 скора чтобы рынок посчитало не плоским
        if score >= 4:
            is_macd_flat = False # MACD не плоский

        # Считаем количество пересечений MACD и сигнальной линии
        crosses = 0
        for i in range(1, len(macd_hist_15) - 1):
            if macd_hist_15[i] * macd_hist_15[i + 1] <= 0:
                crosses += 1

        # Сравниваем количество пересечений с порогом
        is_frequent_crosses = crosses >= min_crosses

        if is_frequent_crosses:
            logging.info("Пересечения >= 3")

        return is_macd_flat or is_frequent_crosses
