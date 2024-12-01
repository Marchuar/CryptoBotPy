import os
from datetime import datetime

def run_backtesting(strategy, test_data, save_result = True):
    # Запускаем бэктестинг на реальных данных
    signals = []
    for i in range(len(test_data)):
        subset = test_data.iloc[:i+1]  # Передаём данные до текущей строки
        signal = strategy.generate_signal(subset)
        test_data.at[i, 'signal'] = signal

    # Сохраняем результаты если режим включен
    if save_result:
        save_backtest_results(test_data, strategy.__class__.__name__)
    print("Мы не попали в save_backtest_results")
    return test_data

def save_backtest_results(test_data, strategy):
    print("Мы попали в save_backtest_results")
    #Сохраняем результаты бэктестинга в файл
    folder = "strategy_testing/backtesting_results"
    os.makedirs(folder, exist_ok=True)

    # Сохраняем результаты стратегии
    file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{strategy}.csv"
    file_path = os.path.join(folder, file_name)
    try:
        test_data.to_csv(file_path, index=True)
        print(f"Результаты бэктестинга сохранены в файл: {file_path}")
    except Exception as e:
        print(f"Не сохранилось: {e}")