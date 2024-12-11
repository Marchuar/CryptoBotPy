def get_perpetual(exchange, limit=10):
    exchange.options["defaultType"] = "swap"
    markets = exchange.load_markets()
    usdt_perpetual = [
        symbol for symbol, market in markets.items()
        if market["type"] == "swap"
           and symbol.endswith("USDT")
    ]
    if limit:
        usdt_perpetual = usdt_perpetual[:limit]
    return usdt_perpetual

# Добавить споты когда-нибудь