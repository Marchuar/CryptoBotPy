import asyncio
import logging

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
        await asyncio.sleep(900)


async def get_contracts(exchange, limit=10):
    exchange.options["defaultType"] = "swap"
    usdt_contracts = [
        symbol for symbol, market in markets.items()
        if market["type"] == "swap"
           and symbol.endswith("USDT")
    ]
    # Слишком много монет, я подрезаю до 10-ти
    # if limit:
    #    usdt_perpetual = usdt_perpetual[:limit]
    return usdt_perpetual

# Добавить споты когда-нибудь
