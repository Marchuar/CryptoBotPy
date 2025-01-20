import threading

from telegram.ext import CommandHandler, ApplicationBuilder, CallbackQueryHandler

from constants import DEFAULT_ANALYZE_INTERVAL
from loger_setup import setup_logging
from connect import init_connection
import logging
from bot import start, stop, change_timeframe, timeframe_callback
from analyze_market import analyze_market
import time
from sql.commands import db_get_subscribed_users, tg_get_user_timeframe
from sql.connection import initialize_database, initialize_connection_pool
import asyncio

init_connection("bybit")
setup_logging()


def start_analyze():
    """
    Continuously analyze the market at regular intervals.
    """
    while True:
        try:
            logging.info("Starting market analysis...")
            subscribed_users = db_get_subscribed_users()

            # Analyze the market for each subscribed user
            for user_id in subscribed_users:
                asyncio.run(analyze_market(user_id, tg_get_user_timeframe(user_id)))

            # Wait for the specified interval before the next analysis
            logging.info(f"Market analysis completed. Waiting for {DEFAULT_ANALYZE_INTERVAL} seconds...")
            time.sleep(DEFAULT_ANALYZE_INTERVAL)
        except Exception as e:
            logging.error(f"Error in market analysis: {e}")
            time.sleep(10)  # Wait before retrying in case of an error


def run_bot():
    """
    Run the Telegram bot in a blocking manner.
    """
    logging.info("Starting Telegram bot...")
    # TODO убрать в .env
    app = ApplicationBuilder().token("***REMOVED_TG_TOKEN***").build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("timeframe", change_timeframe))
    app.add_handler(CallbackQueryHandler(timeframe_callback))
    app.add_handler(CommandHandler("stop", stop))

    # Run the bot in a blocking manner
    app.run_polling()

def main():
    logging.info("Setting up...")
    initialize_connection_pool()
    initialize_database()

    analyze_thread = threading.Thread(target=start_analyze, daemon=True)
    analyze_thread.start()

    run_bot()


if __name__ == "__main__":
    main()
