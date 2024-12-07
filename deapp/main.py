from telegram.ext import CommandHandler, ApplicationBuilder
from strategies.bb import BBStrategy
from strategies.ema import EMAStrategy
from connect import init_connection
from bot import start, stop, start_ema, start_bb, start_macd
from analyze_market import analyze_market
from strategies.macd import MACDStrategy

init_connection("bybit")

def main():
    print("Starting live analyze...")

    # Определение стратегии
    strategies = [EMAStrategy, BBStrategy, MACDStrategy]

    #Создаём Application
    app = ApplicationBuilder().token("***REMOVED_TG_TOKEN***").build()
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
