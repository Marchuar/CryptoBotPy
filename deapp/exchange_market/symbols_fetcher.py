import asyncio
import logging

from constants import DEFAULT_VOLUME_LIMIT, DEFAULT_ANALYZE_SYMBOLS, \
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
            logging.info(f"Symbols loaded, refresh in {DEFAULT_SYMBOLS_REFRESH_INTERVAL / 360} hours")
            await asyncio.sleep(DEFAULT_SYMBOLS_REFRESH_INTERVAL)


async def clean_markets(exchange, state):
    for symbol, market in list(state.markets.items()):
        if (
                market["type"] != "swap"
                or not symbol.endswith("USDT")
                or not market["contract"] == True
                or not market["active"] == True
        ):
            del state.markets[symbol]
    try:
        ticker = exchange.fetch_tickers()
        for symbol in state.markets:
            if not ticker:
                break
            for ticker_symbol in ticker:
                if symbol == ticker_symbol:
                    symbol_volume = ticker[ticker_symbol].get('quoteVolume', 0)
                    if symbol_volume and symbol_volume <= DEFAULT_VOLUME_LIMIT:
                        del state.markets[symbol]
                        break
                    del ticker[ticker_symbol]
                    break
        logging.info(f"Symbols filter completed, total amount of symbols: {len(state.markets)}")
    except Exception as e:
        logging.error(f"Error during tickers fetch: {e}")
