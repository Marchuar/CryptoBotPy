import logging

from strategies.indicators.adx import ADXIndicator
from back_tests.executor.backtesting import run_testing
from back_tests.executor.test_data_generator import fetch_history_data_from_exchange
from connect import get_connection


def test_from_exchange(
        exchange=get_connection("bybit"),
        strategy=ADXIndicator(),
        symbol="BTCUSDT",
        timeframe="1h",
        since="2024-11-06T00:00:00Z"
):
    logging.info("Загружаем исторические данные из биржи")
    data = fetch_history_data_from_exchange(exchange, symbol, timeframe, since)

    logging.info("Запуск бэктестинга...")
    result = run_testing(strategy, data)

    assert result is not None, "Завершено без результатов"
    logging.info("Тест завершен, йоу")
