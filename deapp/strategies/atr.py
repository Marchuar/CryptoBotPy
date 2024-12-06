import talib


class ATRStrategy:
    def __init__(self, atr_period=14):
        self.name = "ATR"
        self.candles_amount = atr_period * 2
        self.atr_period = atr_period

    def generate_signal(self, df):

        if len(df) < self.candles_amount:
            return "not_enough_candles"

        curr_atr = df['ATR'].iloc[-1]
        print(curr_atr)
        print(df['ATR'].mean())

        if curr_atr < df['ATR'].mean():
            return("Avoid trading.")
        else:
            return("Market volatility is high. Signals are reliable.")

        # Это можно ещё добавить
        # Стоп-лосс: на уровне 1–2 ATR выше текущей цены.
        # Тейк-профит: на уровне 2–3 ATR ниже текущей цены.


    def calculate_indicators(self, df):
        # Указываем индикаторы
        df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=self.atr_period)
        print(df)
        return df