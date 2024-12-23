import logging

from strategies.emaOld import EMAStrategy
from back_tests.executor.test_data_generator import load_data_from_csv
from back_tests.executor.backtesting import run_testing


def test_from_csv(
        strategy=EMAStrategy(),
        file_path="/..."
):
    logging.info("Загружаем данные из CSV")
    data = load_data_from_csv(file_path)
    result = run_testing(strategy, data)

    assert result is not None, "Завершено без результатов"
    logging.info("Тест завершен, йоу")
