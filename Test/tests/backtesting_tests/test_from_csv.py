from strategies.ema import EMAStrategy
from tests.executor.test_data_generator import load_data_from_csv
from tests.executor.backtesting import run_testing


def test_from_csv(
        strategy=EMAStrategy(),
        file_path="/..."
):
    print("Загружаем данные из CSV")
    data = load_data_from_csv(file_path)
    result = run_testing(strategy, data)

    assert result is not None, "Завершено без результатов"
    print("Тест завершен, йоу")
