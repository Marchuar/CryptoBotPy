import logging

from telegram.ext import CommandHandler, ApplicationBuilder

from constants import DEFAULT_ANALYZE_INTERVAL
from strategies.bb import BB
from strategies.ema import EMA
from connect import init_connection
from bot import start, stop, start_ema, start_bb, start_macd
from analyze_market import analyze_market
from strategies.macd import MACD
from loger_setup import setup_logging

init_connection("bybit")
setup_logging()


def main():
    logging.info("Setting up...")

    # Определение стратегии
    strategies = [EMA, MACD, BB]

    # Создаём Application
    app = ApplicationBuilder().token("***REMOVED_TG_TOKEN***").build()
    job_queue = app.job_queue

    # Анализ рынка
    for strategy in strategies:
        # Init strategy
        strategy = strategy()
        # Start analyze
        job_queue.run_repeating(analyze_market, interval=DEFAULT_ANALYZE_INTERVAL, data=strategy)

    # add commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ema", start_ema))
    app.add_handler(CommandHandler("bb", start_bb))
    app.add_handler(CommandHandler("macd", start_macd))
    app.add_handler(CommandHandler("stop", stop))

    # start bot
    app.run_polling()


if __name__ == "__main__":
    main()
