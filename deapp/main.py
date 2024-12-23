from telegram.ext import CommandHandler, ApplicationBuilder
from strategies.indicators.bb import BBIndicator
from strategies.emaOld import EMAStrategy
from connect import init_connection
from bot import start, stop, start_ema, start_bb, start_macd
from analyze_market import analyze_market

init_connection("bybit")


def main():
    print("Setting up...")

    # Определение стратегии
    strategies = [EMAStrategy, BBIndicator]

    # Создаём Application
    app = ApplicationBuilder().token("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c").build()
    job_queue = app.job_queue

    # Анализ рынка
    for strategy in strategies:
        # Init strategy
        strategy = strategy()
        # Start analyze
        job_queue.run_repeating(analyze_market, interval=20, data=strategy)

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
