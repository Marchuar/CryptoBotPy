import logging

import pandas as pd
from back_tests.executor.results_saver import save_results


def load_data_from_csv(file_path):
    # Загрузить данные из CSV
    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def fetch_history_data_from_exchange(
        exchange_connection,
        symbol,
        timeframe,
        since
):
    # Загрузить исторические данные из биржи
    since = exchange_connection.parse8601(since)
    limit = exchange_connection.options.get("fetchOHLCV", {}).get("maxLimit", 200)
    all_data = []

    while True:
        ohlcv = exchange_connection.fetch_ohlcv(symbol, timeframe, since, limit)
        all_data.extend(ohlcv)

        if len(ohlcv) <= 1:
            logging.info("Данные закончились, все свечи выгружены")
            break
        since = ohlcv[-1][0] + 1

        logging.info(f"Загружено {len(ohlcv)} свечей, всего: {len(all_data)}")

    # Преобразование в DataFrame
    df = pd.DataFrame(
        all_data, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    save_results(df)
    return df
