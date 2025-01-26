import ccxt
import logging

connections = {}


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
            logging.error(f"Ошибка соединения с биржей {exchange_name}: {e}")
            raise


def get_connection(exchange_name):
    # Возвращает инициализированное соединение с указанной биржей
    global connections
    if exchange_name not in connections:
        try:
            init_connection(exchange_name)
        except Exception as e:
            logging.error(f"Ошибка соединения с биржей: {e}")
    return connections[exchange_name]
