import logging
import os
import sys
from dotenv import load_dotenv

from constants import DEFAULT_ANALYZE_ALL_SYMBOLS_MODE
from exchange_market.symbols_fetcher import markets_loader, MarketState
from loger_setup import setup_logging
import asyncio
from aiogram import Bot, Dispatcher
from bot import router
from connect import init_connection, get_connection
from analyze_market import start_analyze
from sql.connection import initialize_database, initialize_connection_pool

load_dotenv()
init_connection("bybit")
exchange = get_connection("bybit")
setup_logging()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    logging.info("Setting up...")

    initialize_connection_pool()
    initialize_database()

    dp.include_router(router)

    state = MarketState()

    await asyncio.gather(
        dp.start_polling(bot),
        markets_loader(exchange, DEFAULT_ANALYZE_ALL_SYMBOLS_MODE, state),
        start_analyze(bot, exchange, state),
        return_exceptions=True
    )


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
