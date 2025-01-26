import ccxt
import logging

connections = {}
markets_cache = {}


def init_connection(exchange_name):
    # Инициализирует соединение с указанной биржей
    global connections
    if exchange_name not in connections:
        exchanges = {
            'bybit': ccxt.bybit(),
            'binance': ccxt.binance()
        }
        try:
            connections[exchange_name] = exchanges[exchange_name]
        except Exception as e:
            logging.error(f"Exchange connection error {exchange_name}: {e}")
            raise

    # Выгружаем рынки из биржи
    if exchange_name not in markets_cache:
        try:
            markets_cache[exchange_name] = connections[exchange_name].load_markets()
        except ccxt.NetworkError as e:
            logging.error(f"Network error when uploading data from the exchange {exchange_name}: {e}")
            raise
        except ccxt.BaseError as e:
            logging.error(f"Exchange error when uploading data {exchange_name}: {e}")
            raise

    return connections[exchange_name]


def get_connection(exchange_name):
    # Возвращает инициализированное соединение с указанной биржей
    global connections
    if exchange_name not in connections:
        try:
            init_connection(exchange_name)
        except Exception as e:
            logging.error(f"Exchange connection error: {e}")
    return connections[exchange_name]


def get_markets(exchange_name):
    # Выгружаем рынки указанной биржи, если они еще не загружены
    global markets_cache
    if exchange_name not in markets_cache:
        exchange = get_connection(exchange_name)
        markets_cache[exchange_name] = exchange.load_markets()
    return markets_cache[exchange_name]
