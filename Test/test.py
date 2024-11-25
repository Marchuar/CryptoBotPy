import ccxt
import time
import json
from datetime import datetime

exchangeBB = ccxt.bybit()
exchangeBin = ccxt.binance()

symbol = "BTC/USDT"

while True:
    ticker = exchangeBB.fetch_ticker(symbol)
    lastTicker = ticker["last"]

    data = {
        "symbol": symbol,
        "price": lastTicker,
        "time": datetime.now().isoformat(),
    }

    with open("Test/prices.json", "w") as file:
        json.dump(data, file, indent=4)

    time.sleep(5)
