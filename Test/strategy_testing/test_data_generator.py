import pandas as pd
from strategy_testing.results_saver import save_results

from connect import get_connection


def load_data_from_csv(file_path):
    # Загрузить данные из CSV
    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def fetch_history_data_from_exchange(
        symbol="BTCUSDT", timeframe="30m", since = None
):
    # Загрузить исторические данные из биржи
    exchange = get_connection("bybit")
    since = exchange.parse8601("2024-09-15T00:00:00Z")
    limit = exchange.options.get("fetchOHLCV", {}).get("maxLimit", 200)
    all_data = []

    while True:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        all_data.extend(ohlcv)

        if len(ohlcv) <= 1:
            print("Данные закончились, все свечи выгружены")
            break
        since = ohlcv[-1][0] + 1

        print(f"Загружено {len(ohlcv)} свечей, всего: {len(all_data)}")

    # Преобразование в DataFrame
    df = pd.DataFrame(
        all_data, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    save_results(df)
    return df
