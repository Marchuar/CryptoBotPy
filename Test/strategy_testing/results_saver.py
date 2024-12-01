import os
from datetime import datetime

def save_results(test_data, strategy = None):
    print("Мы попали в save_results")
    #Сохраняем результаты в файл
    if strategy is None:
        folder = "strategy_testing/exchange_candles_history_results"
    else:
        folder = "strategy_testing/backtesting_results"
    os.makedirs(folder, exist_ok=True)

    # Сохраняем результаты стратегии
    file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{strategy}.csv"
    file_path = os.path.join(folder, file_name)
    try:
        test_data.to_csv(file_path, index=True)
        print(f"Результаты сохранены в файл: {file_path}")
    except Exception as e:
        print(f"Не сохранилось: {e}")