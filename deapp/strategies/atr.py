import talib


class ATRStrategy:
    def __init__(self, atr_period=14):
        self.name = "ATR"
        self.candles_amount = atr_period * 2
        self.atr_period = atr_period

    @staticmethod
    def calculate_points(curr_atr, price_now):
        points = []

        long = {
            "trend": "long",
            "stop_loss": price_now - curr_atr * 1.5,
            "take_profit": price_now + curr_atr * 3
        }
        short = {
            "trend": "short",
            "stop_loss": price_now + curr_atr * 1.5,
            "take_profit": price_now - curr_atr * 3
        }

        points.append(long)
        points.append(short)
        return points

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        curr_atr = df['ATR'].iloc[-1]
        print(curr_atr)
        print(df['ATR'].mean())

        if curr_atr < df['ATR'].mean():
            return "Avoid trading."
        else:
            # Считаем Stop_Loss и Take_Profit на тренды long и short
            points = self.calculate_points(curr_atr, df["close"].iloc[-1])
            return "Market volatility is high. Signals are reliable. " + str(points)

        # Это можно ещё добавить
        # Стоп-лосс: на уровне 1–2 ATR выше текущей цены.
        # Тейк-профит: на уровне 2–3 ATR ниже текущей цены.


    def calculate_indicators(self, df):
        # Указываем индикаторы
        df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=self.atr_period)
        print(df)
        return df
