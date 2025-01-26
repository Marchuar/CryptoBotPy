import logging
import sys

from exchange_market.symbols_fetcher import markets_loader
from loger_setup import setup_logging
import asyncio
from aiogram import Bot, Dispatcher
from bot import router
from connect import init_connection, get_connection
from analyze_market import start_analyze
from sql.connection import initialize_database, initialize_connection_pool

init_connection("bybit")
exchange = get_connection("bybit")
setup_logging()
BOT_TOKEN = "***REMOVED_TG_TOKEN***"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
lock = asyncio.Lock()

async def main():
    logging.info("Setting up...")

    initialize_connection_pool()
    initialize_database()

    dp.include_router(router)

    await asyncio.gather(
        dp.start_polling(bot),
        start_analyze(bot, exchange, lock),
        markets_loader(exchange, lock),
        return_exceptions=True
    )


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
