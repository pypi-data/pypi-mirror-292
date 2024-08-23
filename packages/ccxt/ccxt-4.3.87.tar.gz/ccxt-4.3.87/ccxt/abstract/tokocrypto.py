from ccxt.base.types import Entry


class ImplicitAPI:
    binance_get_ping = binanceGetPing = Entry('ping', 'binance', 'GET', {'cost': 1})
    binance_get_time = binanceGetTime = Entry('time', 'binance', 'GET', {'cost': 1})
    binance_get_depth = binanceGetDepth = Entry('depth', 'binance', 'GET', {'cost': 1, 'byLimit': [[100, 1], [500, 5], [1000, 10], [5000, 50]]})
    binance_get_trades = binanceGetTrades = Entry('trades', 'binance', 'GET', {'cost': 1})
    binance_get_aggtrades = binanceGetAggTrades = Entry('aggTrades', 'binance', 'GET', {'cost': 1})
    binance_get_historicaltrades = binanceGetHistoricalTrades = Entry('historicalTrades', 'binance', 'GET', {'cost': 5})
    binance_get_klines = binanceGetKlines = Entry('klines', 'binance', 'GET', {'cost': 1})
    binance_get_ticker_24hr = binanceGetTicker24hr = Entry('ticker/24hr', 'binance', 'GET', {'cost': 1, 'noSymbol': 40})
    binance_get_ticker_price = binanceGetTickerPrice = Entry('ticker/price', 'binance', 'GET', {'cost': 1, 'noSymbol': 2})
    binance_get_ticker_bookticker = binanceGetTickerBookTicker = Entry('ticker/bookTicker', 'binance', 'GET', {'cost': 1, 'noSymbol': 2})
    binance_get_exchangeinfo = binanceGetExchangeInfo = Entry('exchangeInfo', 'binance', 'GET', {'cost': 10})
    binance_put_userdatastream = binancePutUserDataStream = Entry('userDataStream', 'binance', 'PUT', {'cost': 1})
    binance_post_userdatastream = binancePostUserDataStream = Entry('userDataStream', 'binance', 'POST', {'cost': 1})
    binance_delete_userdatastream = binanceDeleteUserDataStream = Entry('userDataStream', 'binance', 'DELETE', {'cost': 1})
    public_get_open_v1_common_time = publicGetOpenV1CommonTime = Entry('open/v1/common/time', 'public', 'GET', {'cost': 1})
    public_get_open_v1_common_symbols = publicGetOpenV1CommonSymbols = Entry('open/v1/common/symbols', 'public', 'GET', {'cost': 1})
    public_get_open_v1_market_depth = publicGetOpenV1MarketDepth = Entry('open/v1/market/depth', 'public', 'GET', {'cost': 1})
    public_get_open_v1_market_trades = publicGetOpenV1MarketTrades = Entry('open/v1/market/trades', 'public', 'GET', {'cost': 1})
    public_get_open_v1_market_agg_trades = publicGetOpenV1MarketAggTrades = Entry('open/v1/market/agg-trades', 'public', 'GET', {'cost': 1})
    public_get_open_v1_market_klines = publicGetOpenV1MarketKlines = Entry('open/v1/market/klines', 'public', 'GET', {'cost': 1})
    private_get_open_v1_orders_detail = privateGetOpenV1OrdersDetail = Entry('open/v1/orders/detail', 'private', 'GET', {'cost': 1})
    private_get_open_v1_orders = privateGetOpenV1Orders = Entry('open/v1/orders', 'private', 'GET', {'cost': 1})
    private_get_open_v1_account_spot = privateGetOpenV1AccountSpot = Entry('open/v1/account/spot', 'private', 'GET', {'cost': 1})
    private_get_open_v1_account_spot_asset = privateGetOpenV1AccountSpotAsset = Entry('open/v1/account/spot/asset', 'private', 'GET', {'cost': 1})
    private_get_open_v1_orders_trades = privateGetOpenV1OrdersTrades = Entry('open/v1/orders/trades', 'private', 'GET', {'cost': 1})
    private_get_open_v1_withdraws = privateGetOpenV1Withdraws = Entry('open/v1/withdraws', 'private', 'GET', {'cost': 1})
    private_get_open_v1_deposits = privateGetOpenV1Deposits = Entry('open/v1/deposits', 'private', 'GET', {'cost': 1})
    private_get_open_v1_deposits_address = privateGetOpenV1DepositsAddress = Entry('open/v1/deposits/address', 'private', 'GET', {'cost': 1})
    private_post_open_v1_orders = privatePostOpenV1Orders = Entry('open/v1/orders', 'private', 'POST', {'cost': 1})
    private_post_open_v1_orders_cancel = privatePostOpenV1OrdersCancel = Entry('open/v1/orders/cancel', 'private', 'POST', {'cost': 1})
    private_post_open_v1_orders_oco = privatePostOpenV1OrdersOco = Entry('open/v1/orders/oco', 'private', 'POST', {'cost': 1})
    private_post_open_v1_withdraws = privatePostOpenV1Withdraws = Entry('open/v1/withdraws', 'private', 'POST', {'cost': 1})
    private_post_open_v1_user_data_stream = privatePostOpenV1UserDataStream = Entry('open/v1/user-data-stream', 'private', 'POST', {'cost': 1})
