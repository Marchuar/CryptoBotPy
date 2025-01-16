from telegram.ext import CommandHandler, ApplicationBuilder, CallbackQueryHandler

from constants import DEFAULT_ANALYZE_INTERVAL
from loger_setup import setup_logging
from connect import init_connection
import logging
from bot import start, stop, change_timeframe, timeframe_callback
from analyze_market import analyze_market
from strategies.universal import UniversalStrategy

init_connection("bybit")
setup_logging()


def main():
    logging.info("Setting up...")

    # Определение стратегии
    strategies = [UniversalStrategy]
    # Создаём Application
    app = ApplicationBuilder().token("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c").build()
    job_queue = app.job_queue

    # Анализ рынка
    for strategy in strategies:
        # Init strategy
        strategy = strategy()
        # Start analyze
        job_queue.run_repeating(analyze_market, interval=DEFAULT_ANALYZE_INTERVAL, data=strategy)

    # add commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("timeframe", change_timeframe))
    app.add_handler(CallbackQueryHandler(timeframe_callback))
    app.add_handler(CommandHandler("stop", stop))

    # start bot
    app.run_polling()


if __name__ == "__main__":
    main()
