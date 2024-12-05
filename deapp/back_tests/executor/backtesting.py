from back_tests.executor.results_saver import save_results


def run_testing(strategy, test_data, save_result=True):
    # Запускаем бэктестинг на реальных данных
    if len(test_data) < strategy.candles_amount:
        raise ValueError("Недостаточно данных")

    test_data = strategy.calculate_indicators(test_data)
    test_data['signal'] = "no_signal"

    for i in range(strategy.candles_amount, len(test_data) + 1):
        subset = test_data.iloc[i - strategy.candles_amount:i]
        signal = strategy.generate_signal(subset)
        test_data.at[i - 1, 'signal'] = signal

    # Сохраняем результаты если режим сохранения включен
    if save_result:
        save_results(test_data, strategy.__class__.__name__)
    return test_data
