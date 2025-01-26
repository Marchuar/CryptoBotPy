import asyncio
import logging

from constants import DEFAULT_VOLUME_HOURS, DEFAULT_VOLUME_LIMIT

markets = {}


async def markets_loader(exchange, lock):
    global markets
    while True:
        async with lock:
            logging.info("Обновляем список символов...")
            try:
                markets = exchange.load_markets(True)
                logging.info(f"Список сиволов обновлён. Найдено {len(markets)} символов.")
            except Exception as e:
                logging.error(f"Ошибка обновления символов: {e}")
        await clean_markets(exchange, lock)
        await asyncio.sleep(900)


async def clean_markets(exchange, lock):
    global markets
    async with lock:
        for symbol, market in list(markets.items()):
            if (
                    market["type"] != "swap"
                    or not symbol.endswith("USDT")
                    or not market["contract"] == True  # Так и не понял правильно ли это
                    or not market["active"] == True
            ):
                del markets[symbol]
                continue
            else:
                volume = await filter_by_volume(exchange, symbol)
                if not volume or volume <= DEFAULT_VOLUME_LIMIT:
                    logging.debug(f"Символ {symbol} не соответствует условиям объёма. Удаляем.")
                    del markets[symbol]


async def filter_by_volume(exchange, symbol, timeframe='1h', hours=DEFAULT_VOLUME_HOURS):
    try:
        # Загружаем OHLCV данные
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=hours)
        if not ohlcv:
            logging.warn(f"Нет данных для символа {symbol}")
            return None
        elif len(ohlcv) < hours:
            logging.warn(f"Недостаточно свечей для расчета обьема для символа {symbol}")
            return None
        else:
            total_volume = sum([candle[5] for candle in ohlcv])
            logging.debug(f"Общий объём за последние {hours} часов для {symbol}: {total_volume}")
            return total_volume
    except Exception as e:
        logging.error(f"Ошибка при фильтрации объёма: {e}")
        return None
