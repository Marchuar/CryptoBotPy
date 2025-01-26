import logging


class CVDIndicator:
    def __init__(self):
        self.name = "CVD"
        self.candles_amount = 1  # Для CVD требуется минимум одна свеча

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        logging.info(f"Generate signal for {self.name} strategy")

        # Текущие и предыдущие значения CVD
        curr_cvd = df["CVD"].iloc[-1]
        prev_cvd = df["CVD"].iloc[-2]

        # Текущая и предыдущая цены закрытия
        curr_close = df["close"].iloc[-1]
        prev_close = df["close"].iloc[-2]

        # Проверка на дивергенции
        if curr_close > prev_close and curr_cvd < prev_cvd:
            return "short"  # Медвежья дивергенция
        elif curr_close < prev_close and curr_cvd > prev_cvd:
            return "long"  # Бычья дивергенция
        else:
            return "no_signal"

    def calculate_indicators(self, df):
        logging.info(f"Calculation {self.name} strategy")

        if "CVD" not in df.columns:
            # Рассчитываем дельту объема для каждой свечи
            df['cvd_delta'] = df['volume'] * (df['close'] - df['open']).apply(lambda x: 1 if x > 0 else -1)

            # Считаем кумулятивную сумму дельты объема
            df['CVD'] = df['cvd_delta'].cumsum()

        return df