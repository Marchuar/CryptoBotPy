import asyncio
import logging
from constants import DEFAULT_VOLUME_HOURS, DEFAULT_VOLUME_LIMIT, DEFAULT_ANALYZE_SYMBOLS, \
    DEFAULT_SYMBOLS_REFRESH_INTERVAL


class MarketState:
    def __init__(self):
        self.markets = {}
        self.lock = asyncio.Lock()


async def markets_loader(exchange, all_symbols_mode, state):
    async with state.lock:
        while True:
            if not all_symbols_mode:
                logging.info("Default symbols mode enabled")
                state.markets.clear()
                state.markets.update({symbol: {"active": True} for symbol in DEFAULT_ANALYZE_SYMBOLS})
                print(f"Текущий маркет: {state.markets}")
            else:
                logging.info("Loading symbols list...")
                try:
                    state.markets.clear()
                    state.markets.update(exchange.load_markets(True))
                    logging.info(f"Symbols list loaded. {len(state.markets)} symbols were found.")
                except Exception as e:
                    logging.error(f"Symbols loading error: {e}")
                await clean_markets(exchange, state)
            logging.info(f"Symbols loaded, refresh in {DEFAULT_SYMBOLS_REFRESH_INTERVAL / 60} mins")
            await asyncio.sleep(DEFAULT_SYMBOLS_REFRESH_INTERVAL)


async def clean_markets(exchange, state):
    updated_markets = {}

    for symbol, market in list(state.markets.items()):
        # Преобразуем символ, удаляя "/" и ":USDT"
        cleaned_symbol = symbol.replace("/", "").replace(":USDT", "")

        # Проверяем условия для фильтрации
        if (
                market["type"] != "swap"
                or not cleaned_symbol.endswith("USDT")
                or not market["contract"]
                or not market["active"]
        ):
            continue  # Пропускаем символ, если он не соответствует критериям

        # Извлекаем объем для очищенного символа
        volume = await extract_volume(exchange, symbol)
        if volume and volume > DEFAULT_VOLUME_LIMIT:
            updated_markets[cleaned_symbol] = market  # Сохраняем символ с очищенным названием

    # Обновляем состояние markets
    state.markets = updated_markets
    logging.info(f"Symbols filter completed, total amount of symbols: {len(state.markets)}")


async def extract_volume(exchange, symbol, timeframe='1h', hours=DEFAULT_VOLUME_HOURS):
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
            total_volume = sum([candle[hours - 1] for candle in ohlcv])
            return total_volume
    except Exception as e:
        logging.error(f"Ошибка при фильтрации объёма: {e}")
        return None
