import pandas as pd
from connect import get_connection


def load_data_from_csv(file_path):
    # Загрузить данные из CSV
    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def fetch_history_data_from_exchange(
    symbol="BTCUSDT", timeframe="1m", limit=15, since=None
):
    # Загрузить исторические данные из биржи
    exchange = get_connection("bybit")
    since = exchange.parse8601("2024-09-01T00:00:00Z")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
    df = pd.DataFrame(
        ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df
