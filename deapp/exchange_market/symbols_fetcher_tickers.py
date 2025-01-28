import asyncio
import logging
from constants import DEFAULT_VOLUME_LIMIT, DEFAULT_ANALYZE_SYMBOLS, \
    DEFAULT_SYMBOLS_REFRESH_INTERVAL


class MarketState:
    def __init__(self):
        self.tickers = {}
        self.lock = asyncio.Lock()


async def tickers_loader(exchange, all_symbols_mode, state):
    async with state.lock:
        while True:
            if not all_symbols_mode:
                logging.info("Default symbols mode enabled")
                state.tickers.clear()
                state.tickers.update({symbol: {"active": True} for symbol in DEFAULT_ANALYZE_SYMBOLS})
                print(f"Текущий тикер: {state.tickers}")
            else:
                logging.info("Loading symbols list...")
                try:
                    state.tickers.clear()
                    state.tickers.update(exchange.fetch_tickers())
                    logging.info(f"Symbols list loaded. {len(state.tickers)} symbols were found.")
                except Exception as e:
                    logging.error(f"Symbols loading error: {e}")
                await clean_tickers(exchange, state)
            logging.info(f"Symbols loaded, refresh in {DEFAULT_SYMBOLS_REFRESH_INTERVAL / 60} mins")
            await asyncio.sleep(DEFAULT_SYMBOLS_REFRESH_INTERVAL)


async def clean_tickers(exchange, state):
    for symbol, ticker in list(state.tickers.items()):
        if (
                not symbol.endswith("USDT")
        ):
            del state.tickers[symbol]
            continue
        else:
            try:
                volume = ticker["quoteVolume"]
                if not volume or volume <= DEFAULT_VOLUME_LIMIT:
                    del state.tickers[symbol]
            except Exception as e:
                logging.error(f"Ошибка в volume: {e}")
    logging.info(f"Symbols filter completed, total amount of symbols: {len(state.tickers)}")