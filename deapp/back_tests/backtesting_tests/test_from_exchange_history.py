import logging

from back_tests.executor.backtesting import run_testing
from back_tests.executor.test_data_generator import fetch_history_data_from_exchange
from connect import get_connection
from strategies.universal import UniversalStrategy


def test_from_exchange(
        exchange=get_connection("bybit"),
        strategy=UniversalStrategy(),
        symbol="BTCUSDT",
        timeframe="1h",
        since="2024-12-01T00:00:00Z"
):
    logging.info("Загружаем исторические данные из биржи")
    data = fetch_history_data_from_exchange(exchange, symbol, timeframe, since)

    logging.info("Запуск бэктестинга...")
    result = run_testing(strategy, data)

    assert result is not None, "Завершено без результатов"
    logging.info("Тест завершен, йоу")
