import ccxt
import json
from datetime import datetime

pricesList = []

# definition of exchange
exchangeBB = ccxt.bybit()
exchangeBin = ccxt.binance()

# get all markets
marketsBB = exchangeBB.load_markets()


# get price function
def getPriceInfo(symbol):
    ticker = exchangeBB.fetch_ticker(symbol)
    lastTicker = ticker["last"]

    newPrice = {
        "symbol": symbol,
        "price": lastTicker,
        "time": datetime.now().isoformat(),
    }

    pricesList.append(newPrice)


# get 20 prices
def get20Prices():
    i = 0
    for symbol in marketsBB:
        if i < 10:
            getPriceInfo(symbol)
        else:
            break


# save data in json file
with open("Test/prices.json", "w") as file:
    json.dump(pricesList, file, indent=4)
