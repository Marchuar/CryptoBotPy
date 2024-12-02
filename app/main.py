from telegram.ext import Updater, CommandHandler
import threading
from strategies.ema import EMAStrategy
from connect import init_connection
from bot import start, stop, orders
from analyze_market import analyze_market

init_connection("bybit")


def main():
    print("Запуск анализа реального рынка...")

    # Определение стратегии
    strategy = EMAStrategy()

    # Анализ рынка
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
