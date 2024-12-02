from connect import init_connection, get_connection
from datetime import datetime, timedelta

# Достаем подключение к бирже
exchange = get_connection('bybit')

symbol = "BTC/USDT"


def getOrdersInfo():
    # 5 minutes
    since = int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000)

    # get trades
    trades = exchange.fetch_trades(symbol, since)

    # get all orders count
    totalOrders = len(trades)

    # get long and short orders
    longOrders = [trade for trade in trades if trade["side"] == "buy"]
    shortOrders = [trade for trade in trades if trade["side"] == "sell"]

    # get lond and short count
    longCount = len(longOrders)
    shortCount = len(shortOrders)

    longPercent = str(longCount / totalOrders * 100) + "%"
    shortPercent = str(shortCount / totalOrders * 100) + "%"

    response = {
        "Symbol": symbol,
        "All Orders": totalOrders,
        "Long Orders count": longCount,
        "Short Orders count": shortCount,
        "Long Orders percent": longPercent,
        "Short Orders percent": shortPercent,
    }

    return response
