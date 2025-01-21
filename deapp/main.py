import logging
from loger_setup import setup_logging
import asyncio
import time
from aiogram import Bot, Dispatcher
from bot import router
from constants import DEFAULT_ANALYZE_INTERVAL
from connect import init_connection
from analyze_market import analyze_market
from sql.commands import db_get_subscribed_users, tg_get_user_timeframe
from sql.connection import initialize_database, initialize_connection_pool

init_connection("bybit")
setup_logging()
BOT_TOKEN = "***REMOVED_TG_TOKEN***"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def start_analyze():
    """
    Continuously analyze the market at regular intervals.
    """
    while True:
        try:
            logging.info("Starting market analysis...")
            subscribed_users = db_get_subscribed_users()

            tasks = []
            for user_id in subscribed_users:
                task = asyncio.create_task(
                    analyze_market(user_id, tg_get_user_timeframe(user_id), bot)
                )
                tasks.append(task)

            # Дожидаемся завершения всех задач
            await asyncio.gather(*tasks)

            # Wait for the specified interval before the next analysis
            logging.info(f"Market analysis completed. Waiting for {DEFAULT_ANALYZE_INTERVAL} seconds...")
            time.sleep(DEFAULT_ANALYZE_INTERVAL)
        except Exception as e:
            logging.error(f"Error in market analysis: {e}")
            time.sleep(10)  # Wait before retrying in case of an error


async def main():
    logging.info("Setting up...")

    initialize_connection_pool()
    initialize_database()

    dp.include_router(router)
    await dp.start_polling(bot)

   # await asyncio.gather(
   #     # Ваша фоновая задача
   #     dp.start_polling(bot), start_analyze()  # Поллинг бота
   # )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('End')
