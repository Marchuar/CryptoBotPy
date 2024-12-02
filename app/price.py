from connect import get_connection, get_markets
from datetime import datetime

pricesList = []

# Коннект к бирже
exchangeBB = get_connection('bybit')

# Достаем рынки биржи
marketsBB = get_markets('bybit')


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


# get 10 prices
def get10Prices():
    i = 0
    for symbol in marketsBB:
        if i < 10:
            getPriceInfo(symbol)

            i = i + 1
        else:
            break


# save data in json file
# with open("app/prices.json", "w") as file:
    # json.dump(pricesList, file, indent=4)
