from telegram.ext import Updater, CommandHandler
import threading
from strategies.ema import EMAStrategy
from strategy_testing.test_data_generator import (
    load_data_from_csv,
    fetch_history_data_from_exchange,
)
from connect import init_connection
from strategy_testing.backtesting import run_backtesting
from bot import start, stop, orders
from analyze_market import analyze_market

init_connection("bybit")


def main():
    print("Выберите режим:")
    print("1. Бэктестинг")
    print("2. Анализ реального рынка")

    mode = input("Введите номер режима: ")

    if mode == "1":
        print("Поехали тестить...")
        print("1. Загрузить данные из CSV")
        print("2. Загрузить данные с биржи")

        data_source = input("Введите номер источника данных: ")

        if data_source == "1":
            file_path = input("Введите пусть к CSV файлу: ")
            data = load_data_from_csv(file_path)
        elif data_source == "2":
            data = fetch_history_data_from_exchange()

        strategy = EMAStrategy()

        print("Запуск бэктестинга...")
        run_backtesting(strategy, data)
    if mode == "2":
        print("Запуск анализа реального рынка...")

        strategy = EMAStrategy()

        # analyze market
        threading.Thread(target=analyze_market, args=(strategy,), daemon=True).start()

        updater = Updater("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c")
        dp = updater.dispatcher

        # add commands
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("stop", stop))
        dp.add_handler(CommandHandler("orders", orders))

        # start bot
        updater.start_polling()
        updater.idle()


if __name__ == "__main__":
    main()
