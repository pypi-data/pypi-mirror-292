from ccxt.base.types import Entry


class ImplicitAPI:
    v1_public_get_assets = v1PublicGetAssets = Entry('assets', ['v1', 'public'], 'GET', {})
    v1_public_get_assets_assets = v1PublicGetAssetsAssets = Entry('assets/{assets}', ['v1', 'public'], 'GET', {})
    v1_public_get_assets_asset_networks = v1PublicGetAssetsAssetNetworks = Entry('assets/{asset}/networks', ['v1', 'public'], 'GET', {})
    v1_public_get_instruments = v1PublicGetInstruments = Entry('instruments', ['v1', 'public'], 'GET', {})
    v1_public_get_instruments_instrument = v1PublicGetInstrumentsInstrument = Entry('instruments/{instrument}', ['v1', 'public'], 'GET', {})
    v1_public_get_instruments_instrument_quote = v1PublicGetInstrumentsInstrumentQuote = Entry('instruments/{instrument}/quote', ['v1', 'public'], 'GET', {})
    v1_public_get_instruments_instrument_funding = v1PublicGetInstrumentsInstrumentFunding = Entry('instruments/{instrument}/funding', ['v1', 'public'], 'GET', {})
    v1_public_get_instruments_instrument_candles = v1PublicGetInstrumentsInstrumentCandles = Entry('instruments/{instrument}/candles', ['v1', 'public'], 'GET', {})
    v1_private_get_orders = v1PrivateGetOrders = Entry('orders', ['v1', 'private'], 'GET', {})
    v1_private_get_orders_id = v1PrivateGetOrdersId = Entry('orders/{id}', ['v1', 'private'], 'GET', {})
    v1_private_get_portfolios = v1PrivateGetPortfolios = Entry('portfolios', ['v1', 'private'], 'GET', {})
    v1_private_get_portfolios_portfolio = v1PrivateGetPortfoliosPortfolio = Entry('portfolios/{portfolio}', ['v1', 'private'], 'GET', {})
    v1_private_get_portfolios_portfolio_detail = v1PrivateGetPortfoliosPortfolioDetail = Entry('portfolios/{portfolio}/detail', ['v1', 'private'], 'GET', {})
    v1_private_get_portfolios_portfolio_summary = v1PrivateGetPortfoliosPortfolioSummary = Entry('portfolios/{portfolio}/summary', ['v1', 'private'], 'GET', {})
    v1_private_get_portfolios_portfolio_balances = v1PrivateGetPortfoliosPortfolioBalances = Entry('portfolios/{portfolio}/balances', ['v1', 'private'], 'GET', {})
    v1_private_get_portfolios_portfolio_balances_asset = v1PrivateGetPortfoliosPortfolioBalancesAsset = Entry('portfolios/{portfolio}/balances/{asset}', ['v1', 'private'], 'GET', {})
    v1_private_get_portfolios_portfolio_positions = v1PrivateGetPortfoliosPortfolioPositions = Entry('portfolios/{portfolio}/positions', ['v1', 'private'], 'GET', {})
    v1_private_get_portfolios_portfolio_positions_instrument = v1PrivateGetPortfoliosPortfolioPositionsInstrument = Entry('portfolios/{portfolio}/positions/{instrument}', ['v1', 'private'], 'GET', {})
    v1_private_get_portfolios_fills = v1PrivateGetPortfoliosFills = Entry('portfolios/fills', ['v1', 'private'], 'GET', {})
    v1_private_get_portfolios_portfolio_fills = v1PrivateGetPortfoliosPortfolioFills = Entry('portfolios/{portfolio}/fills', ['v1', 'private'], 'GET', {})
    v1_private_get_transfers = v1PrivateGetTransfers = Entry('transfers', ['v1', 'private'], 'GET', {})
    v1_private_get_transfers_transfer_uuid = v1PrivateGetTransfersTransferUuid = Entry('transfers/{transfer_uuid}', ['v1', 'private'], 'GET', {})
    v1_private_post_orders = v1PrivatePostOrders = Entry('orders', ['v1', 'private'], 'POST', {})
    v1_private_post_portfolios = v1PrivatePostPortfolios = Entry('portfolios', ['v1', 'private'], 'POST', {})
    v1_private_post_portfolios_margin = v1PrivatePostPortfoliosMargin = Entry('portfolios/margin', ['v1', 'private'], 'POST', {})
    v1_private_post_portfolios_transfer = v1PrivatePostPortfoliosTransfer = Entry('portfolios/transfer', ['v1', 'private'], 'POST', {})
    v1_private_post_transfers_withdraw = v1PrivatePostTransfersWithdraw = Entry('transfers/withdraw', ['v1', 'private'], 'POST', {})
    v1_private_post_transfers_address = v1PrivatePostTransfersAddress = Entry('transfers/address', ['v1', 'private'], 'POST', {})
    v1_private_post_transfers_create_counterparty_id = v1PrivatePostTransfersCreateCounterpartyId = Entry('transfers/create-counterparty-id', ['v1', 'private'], 'POST', {})
    v1_private_post_transfers_validate_counterparty_id = v1PrivatePostTransfersValidateCounterpartyId = Entry('transfers/validate-counterparty-id', ['v1', 'private'], 'POST', {})
    v1_private_post_transfers_withdraw_counterparty = v1PrivatePostTransfersWithdrawCounterparty = Entry('transfers/withdraw/counterparty', ['v1', 'private'], 'POST', {})
    v1_private_put_orders_id = v1PrivatePutOrdersId = Entry('orders/{id}', ['v1', 'private'], 'PUT', {})
    v1_private_put_portfolios_portfolio = v1PrivatePutPortfoliosPortfolio = Entry('portfolios/{portfolio}', ['v1', 'private'], 'PUT', {})
    v1_private_delete_orders = v1PrivateDeleteOrders = Entry('orders', ['v1', 'private'], 'DELETE', {})
    v1_private_delete_orders_id = v1PrivateDeleteOrdersId = Entry('orders/{id}', ['v1', 'private'], 'DELETE', {})
