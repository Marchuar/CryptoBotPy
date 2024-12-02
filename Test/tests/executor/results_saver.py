import os
from datetime import datetime


def save_results(test_data, strategy=None):
    print("Идет сохранение файла...")
    # Сохраняем результаты в файл
    if strategy is None:
        folder = "backtesting_tests/exchange_candles_history_results"
        file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_exchange-history.csv"
    else:
        folder = "backtesting_tests/strategy_test_results"
        file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{strategy}.csv"

    # Сохраняем результаты стратегии
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, file_name)
    try:
        test_data.to_csv(file_path, index=True)
        print(f"Результаты сохранены в файл: {file_path}")
    except Exception as e:
        print(f"Не сохранилось: {e}")
