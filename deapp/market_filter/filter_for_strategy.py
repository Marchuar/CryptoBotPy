import logging


def filter_symbols_for_strategy(exchange, symbols, timeframe, min_candles):
    filtered_symbols = []
    for symbol in symbols:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=min_candles)
            if len(ohlcv) == min_candles:
                filtered_symbols.append(symbol)
        except Exception as e:
            logging.error(f"Error getting data for {symbol}: {e}")
    return filtered_symbols

# Можно будет делать разные фильтры, можно будет закинуть поиск новых монет сюда же