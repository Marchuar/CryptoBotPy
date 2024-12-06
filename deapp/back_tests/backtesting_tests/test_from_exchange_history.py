from strategies.ema import EMAStrategy
from strategies.macd import MACDStrategy
from back_tests.executor.backtesting import run_testing
from back_tests.executor.test_data_generator import fetch_history_data_from_exchange
from connect import get_connection


def test_from_exchange(
        exchange=get_connection("bybit"),
        strategy=MACDStrategy(),
        symbol="BTCUSDT",
        timeframe="1h",
        since="2024-11-06T00:00:00Z"
):
    print("Загружаем исторические данные из биржи")
    data = fetch_history_data_from_exchange(exchange, symbol, timeframe, since)

    print("Запуск бэктестинга...")
    result = run_testing(strategy, data)

    assert result is not None, "Завершено без результатов"
    print("Тест завершен, йоу")
