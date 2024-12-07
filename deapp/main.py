from telegram.ext import CommandHandler, ApplicationBuilder
import threading
from strategies.ema import EMAStrategy
from strategies.atr import ATRStrategy
from strategies.bb import BBStrategy
from connect import init_connection
from bot import start, stop
from analyze_market import analyze_market

init_connection("bybit")

def main():
    print("Starting live analyze...")

    # Определение стратегии
    strategy = BBStrategy()

    #Создаём Application
    app = ApplicationBuilder().token("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c").build()
    job_queue = app.job_queue

    # Анализ рынка
    job_queue.run_repeating(analyze_market, interval=15, data=strategy)

    # add commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))

    # start bot
    app.run_polling()


if __name__ == "__main__":
    main()
