from telegram.ext import Updater, CommandHandler
import threading
from strategies.ema import EMAStrategy
from connect import init_connection
from bot import start, stop
from analyze_market import analyze_market

init_connection("bybit")


def main():
    print("Starting live analyze...")

    # Определение стратегии
    strategy = EMAStrategy()

    # Анализ рынка
    threading.Thread(target=analyze_market, args=(strategy,), daemon=True).start()

    updater = Updater("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c")
    dp = updater.dispatcher

    # add commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    # start bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
