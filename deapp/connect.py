import ccxt

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
        connections[exchange_name] = exchanges[exchange_name]

    # Выгружаем рынки из биржи
    if exchange_name not in markets_cache:
        markets_cache[exchange_name] = connections[exchange_name].load_markets()

    return connections[exchange_name]

def get_connection(exchange_name):
    # Возвращает инициализированное соединение с указанной биржей
    global connections
    if exchange_name not in connections:
        init_connection(exchange_name)
    return connections[exchange_name]

def get_markets(exchange_name):
    # Выгружаем рынки указанной биржи, если они еще не загружены
    global markets_cache
    if exchange_name not in markets_cache:
        exchange = get_connection(exchange_name)
        markets_cache[exchange_name] = exchange.load_markets()
    return markets_cache[exchange_name]
