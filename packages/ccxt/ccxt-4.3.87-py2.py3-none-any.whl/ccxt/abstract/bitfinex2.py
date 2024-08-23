from ccxt.base.types import Entry


class ImplicitAPI:
    public_get_conf_config = publicGetConfConfig = Entry('conf/{config}', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_action_object = publicGetConfPubActionObject = Entry('conf/pub:{action}:{object}', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_action_object_detail = publicGetConfPubActionObjectDetail = Entry('conf/pub:{action}:{object}:{detail}', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_map_object = publicGetConfPubMapObject = Entry('conf/pub:map:{object}', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_map_object_detail = publicGetConfPubMapObjectDetail = Entry('conf/pub:map:{object}:{detail}', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_map_currency_detail = publicGetConfPubMapCurrencyDetail = Entry('conf/pub:map:currency:{detail}', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_map_currency_sym = publicGetConfPubMapCurrencySym = Entry('conf/pub:map:currency:sym', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_map_currency_label = publicGetConfPubMapCurrencyLabel = Entry('conf/pub:map:currency:label', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_map_currency_unit = publicGetConfPubMapCurrencyUnit = Entry('conf/pub:map:currency:unit', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_map_currency_undl = publicGetConfPubMapCurrencyUndl = Entry('conf/pub:map:currency:undl', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_map_currency_pool = publicGetConfPubMapCurrencyPool = Entry('conf/pub:map:currency:pool', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_map_currency_explorer = publicGetConfPubMapCurrencyExplorer = Entry('conf/pub:map:currency:explorer', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_map_currency_tx_fee = publicGetConfPubMapCurrencyTxFee = Entry('conf/pub:map:currency:tx:fee', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_map_tx_method = publicGetConfPubMapTxMethod = Entry('conf/pub:map:tx:method', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_list_object = publicGetConfPubListObject = Entry('conf/pub:list:{object}', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_list_object_detail = publicGetConfPubListObjectDetail = Entry('conf/pub:list:{object}:{detail}', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_list_currency = publicGetConfPubListCurrency = Entry('conf/pub:list:currency', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_list_pair_exchange = publicGetConfPubListPairExchange = Entry('conf/pub:list:pair:exchange', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_list_pair_margin = publicGetConfPubListPairMargin = Entry('conf/pub:list:pair:margin', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_list_pair_futures = publicGetConfPubListPairFutures = Entry('conf/pub:list:pair:futures', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_list_competitions = publicGetConfPubListCompetitions = Entry('conf/pub:list:competitions', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_info_object = publicGetConfPubInfoObject = Entry('conf/pub:info:{object}', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_info_object_detail = publicGetConfPubInfoObjectDetail = Entry('conf/pub:info:{object}:{detail}', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_info_pair = publicGetConfPubInfoPair = Entry('conf/pub:info:pair', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_info_pair_futures = publicGetConfPubInfoPairFutures = Entry('conf/pub:info:pair:futures', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_info_tx_status = publicGetConfPubInfoTxStatus = Entry('conf/pub:info:tx:status', 'public', 'GET', {'cost': 2.7})
    public_get_conf_pub_fees = publicGetConfPubFees = Entry('conf/pub:fees', 'public', 'GET', {'cost': 2.7})
    public_get_platform_status = publicGetPlatformStatus = Entry('platform/status', 'public', 'GET', {'cost': 8})
    public_get_tickers = publicGetTickers = Entry('tickers', 'public', 'GET', {'cost': 2.7})
    public_get_ticker_symbol = publicGetTickerSymbol = Entry('ticker/{symbol}', 'public', 'GET', {'cost': 2.7})
    public_get_tickers_hist = publicGetTickersHist = Entry('tickers/hist', 'public', 'GET', {'cost': 2.7})
    public_get_trades_symbol_hist = publicGetTradesSymbolHist = Entry('trades/{symbol}/hist', 'public', 'GET', {'cost': 2.7})
    public_get_book_symbol_precision = publicGetBookSymbolPrecision = Entry('book/{symbol}/{precision}', 'public', 'GET', {'cost': 1})
    public_get_book_symbol_p0 = publicGetBookSymbolP0 = Entry('book/{symbol}/P0', 'public', 'GET', {'cost': 1})
    public_get_book_symbol_p1 = publicGetBookSymbolP1 = Entry('book/{symbol}/P1', 'public', 'GET', {'cost': 1})
    public_get_book_symbol_p2 = publicGetBookSymbolP2 = Entry('book/{symbol}/P2', 'public', 'GET', {'cost': 1})
    public_get_book_symbol_p3 = publicGetBookSymbolP3 = Entry('book/{symbol}/P3', 'public', 'GET', {'cost': 1})
    public_get_book_symbol_r0 = publicGetBookSymbolR0 = Entry('book/{symbol}/R0', 'public', 'GET', {'cost': 1})
    public_get_stats1_key_size_symbol_side_section = publicGetStats1KeySizeSymbolSideSection = Entry('stats1/{key}:{size}:{symbol}:{side}/{section}', 'public', 'GET', {'cost': 2.7})
    public_get_stats1_key_size_symbol_side_last = publicGetStats1KeySizeSymbolSideLast = Entry('stats1/{key}:{size}:{symbol}:{side}/last', 'public', 'GET', {'cost': 2.7})
    public_get_stats1_key_size_symbol_side_hist = publicGetStats1KeySizeSymbolSideHist = Entry('stats1/{key}:{size}:{symbol}:{side}/hist', 'public', 'GET', {'cost': 2.7})
    public_get_stats1_key_size_symbol_section = publicGetStats1KeySizeSymbolSection = Entry('stats1/{key}:{size}:{symbol}/{section}', 'public', 'GET', {'cost': 2.7})
    public_get_stats1_key_size_symbol_last = publicGetStats1KeySizeSymbolLast = Entry('stats1/{key}:{size}:{symbol}/last', 'public', 'GET', {'cost': 2.7})
    public_get_stats1_key_size_symbol_hist = publicGetStats1KeySizeSymbolHist = Entry('stats1/{key}:{size}:{symbol}/hist', 'public', 'GET', {'cost': 2.7})
    public_get_stats1_key_size_symbol_long_last = publicGetStats1KeySizeSymbolLongLast = Entry('stats1/{key}:{size}:{symbol}:long/last', 'public', 'GET', {'cost': 2.7})
    public_get_stats1_key_size_symbol_long_hist = publicGetStats1KeySizeSymbolLongHist = Entry('stats1/{key}:{size}:{symbol}:long/hist', 'public', 'GET', {'cost': 2.7})
    public_get_stats1_key_size_symbol_short_last = publicGetStats1KeySizeSymbolShortLast = Entry('stats1/{key}:{size}:{symbol}:short/last', 'public', 'GET', {'cost': 2.7})
    public_get_stats1_key_size_symbol_short_hist = publicGetStats1KeySizeSymbolShortHist = Entry('stats1/{key}:{size}:{symbol}:short/hist', 'public', 'GET', {'cost': 2.7})
    public_get_candles_trade_timeframe_symbol_period_section = publicGetCandlesTradeTimeframeSymbolPeriodSection = Entry('candles/trade:{timeframe}:{symbol}:{period}/{section}', 'public', 'GET', {'cost': 2.7})
    public_get_candles_trade_timeframe_symbol_section = publicGetCandlesTradeTimeframeSymbolSection = Entry('candles/trade:{timeframe}:{symbol}/{section}', 'public', 'GET', {'cost': 2.7})
    public_get_candles_trade_timeframe_symbol_last = publicGetCandlesTradeTimeframeSymbolLast = Entry('candles/trade:{timeframe}:{symbol}/last', 'public', 'GET', {'cost': 2.7})
    public_get_candles_trade_timeframe_symbol_hist = publicGetCandlesTradeTimeframeSymbolHist = Entry('candles/trade:{timeframe}:{symbol}/hist', 'public', 'GET', {'cost': 2.7})
    public_get_status_type = publicGetStatusType = Entry('status/{type}', 'public', 'GET', {'cost': 2.7})
    public_get_status_deriv = publicGetStatusDeriv = Entry('status/deriv', 'public', 'GET', {'cost': 2.7})
    public_get_status_deriv_symbol_hist = publicGetStatusDerivSymbolHist = Entry('status/deriv/{symbol}/hist', 'public', 'GET', {'cost': 2.7})
    public_get_liquidations_hist = publicGetLiquidationsHist = Entry('liquidations/hist', 'public', 'GET', {'cost': 80})
    public_get_rankings_key_timeframe_symbol_section = publicGetRankingsKeyTimeframeSymbolSection = Entry('rankings/{key}:{timeframe}:{symbol}/{section}', 'public', 'GET', {'cost': 2.7})
    public_get_rankings_key_timeframe_symbol_hist = publicGetRankingsKeyTimeframeSymbolHist = Entry('rankings/{key}:{timeframe}:{symbol}/hist', 'public', 'GET', {'cost': 2.7})
    public_get_pulse_hist = publicGetPulseHist = Entry('pulse/hist', 'public', 'GET', {'cost': 2.7})
    public_get_pulse_profile_nickname = publicGetPulseProfileNickname = Entry('pulse/profile/{nickname}', 'public', 'GET', {'cost': 2.7})
    public_get_funding_stats_symbol_hist = publicGetFundingStatsSymbolHist = Entry('funding/stats/{symbol}/hist', 'public', 'GET', {'cost': 10})
    public_post_calc_trade_avg = publicPostCalcTradeAvg = Entry('calc/trade/avg', 'public', 'POST', {'cost': 2.7})
    public_post_calc_fx = publicPostCalcFx = Entry('calc/fx', 'public', 'POST', {'cost': 2.7})
    private_post_auth_r_wallets = privatePostAuthRWallets = Entry('auth/r/wallets', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_wallets_hist = privatePostAuthRWalletsHist = Entry('auth/r/wallets/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_orders = privatePostAuthROrders = Entry('auth/r/orders', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_orders_symbol = privatePostAuthROrdersSymbol = Entry('auth/r/orders/{symbol}', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_order_submit = privatePostAuthWOrderSubmit = Entry('auth/w/order/submit', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_order_update = privatePostAuthWOrderUpdate = Entry('auth/w/order/update', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_order_cancel = privatePostAuthWOrderCancel = Entry('auth/w/order/cancel', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_order_multi = privatePostAuthWOrderMulti = Entry('auth/w/order/multi', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_order_cancel_multi = privatePostAuthWOrderCancelMulti = Entry('auth/w/order/cancel/multi', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_orders_symbol_hist = privatePostAuthROrdersSymbolHist = Entry('auth/r/orders/{symbol}/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_orders_hist = privatePostAuthROrdersHist = Entry('auth/r/orders/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_order_symbol_id_trades = privatePostAuthROrderSymbolIdTrades = Entry('auth/r/order/{symbol}:{id}/trades', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_trades_symbol_hist = privatePostAuthRTradesSymbolHist = Entry('auth/r/trades/{symbol}/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_trades_hist = privatePostAuthRTradesHist = Entry('auth/r/trades/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_ledgers_currency_hist = privatePostAuthRLedgersCurrencyHist = Entry('auth/r/ledgers/{currency}/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_ledgers_hist = privatePostAuthRLedgersHist = Entry('auth/r/ledgers/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_info_margin_key = privatePostAuthRInfoMarginKey = Entry('auth/r/info/margin/{key}', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_info_margin_base = privatePostAuthRInfoMarginBase = Entry('auth/r/info/margin/base', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_info_margin_sym_all = privatePostAuthRInfoMarginSymAll = Entry('auth/r/info/margin/sym_all', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_positions = privatePostAuthRPositions = Entry('auth/r/positions', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_position_claim = privatePostAuthWPositionClaim = Entry('auth/w/position/claim', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_position_increase = privatePostAuthWPositionIncrease = Entry('auth/w/position/increase:', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_position_increase_info = privatePostAuthRPositionIncreaseInfo = Entry('auth/r/position/increase/info', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_positions_hist = privatePostAuthRPositionsHist = Entry('auth/r/positions/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_positions_audit = privatePostAuthRPositionsAudit = Entry('auth/r/positions/audit', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_positions_snap = privatePostAuthRPositionsSnap = Entry('auth/r/positions/snap', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_deriv_collateral_set = privatePostAuthWDerivCollateralSet = Entry('auth/w/deriv/collateral/set', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_deriv_collateral_limits = privatePostAuthWDerivCollateralLimits = Entry('auth/w/deriv/collateral/limits', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_offers = privatePostAuthRFundingOffers = Entry('auth/r/funding/offers', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_offers_symbol = privatePostAuthRFundingOffersSymbol = Entry('auth/r/funding/offers/{symbol}', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_funding_offer_submit = privatePostAuthWFundingOfferSubmit = Entry('auth/w/funding/offer/submit', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_funding_offer_cancel = privatePostAuthWFundingOfferCancel = Entry('auth/w/funding/offer/cancel', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_funding_offer_cancel_all = privatePostAuthWFundingOfferCancelAll = Entry('auth/w/funding/offer/cancel/all', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_funding_close = privatePostAuthWFundingClose = Entry('auth/w/funding/close', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_funding_auto = privatePostAuthWFundingAuto = Entry('auth/w/funding/auto', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_funding_keep = privatePostAuthWFundingKeep = Entry('auth/w/funding/keep', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_offers_symbol_hist = privatePostAuthRFundingOffersSymbolHist = Entry('auth/r/funding/offers/{symbol}/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_offers_hist = privatePostAuthRFundingOffersHist = Entry('auth/r/funding/offers/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_loans = privatePostAuthRFundingLoans = Entry('auth/r/funding/loans', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_loans_hist = privatePostAuthRFundingLoansHist = Entry('auth/r/funding/loans/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_loans_symbol = privatePostAuthRFundingLoansSymbol = Entry('auth/r/funding/loans/{symbol}', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_loans_symbol_hist = privatePostAuthRFundingLoansSymbolHist = Entry('auth/r/funding/loans/{symbol}/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_credits = privatePostAuthRFundingCredits = Entry('auth/r/funding/credits', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_credits_hist = privatePostAuthRFundingCreditsHist = Entry('auth/r/funding/credits/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_credits_symbol = privatePostAuthRFundingCreditsSymbol = Entry('auth/r/funding/credits/{symbol}', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_credits_symbol_hist = privatePostAuthRFundingCreditsSymbolHist = Entry('auth/r/funding/credits/{symbol}/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_trades_symbol_hist = privatePostAuthRFundingTradesSymbolHist = Entry('auth/r/funding/trades/{symbol}/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_funding_trades_hist = privatePostAuthRFundingTradesHist = Entry('auth/r/funding/trades/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_info_funding_key = privatePostAuthRInfoFundingKey = Entry('auth/r/info/funding/{key}', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_info_user = privatePostAuthRInfoUser = Entry('auth/r/info/user', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_summary = privatePostAuthRSummary = Entry('auth/r/summary', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_logins_hist = privatePostAuthRLoginsHist = Entry('auth/r/logins/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_permissions = privatePostAuthRPermissions = Entry('auth/r/permissions', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_token = privatePostAuthWToken = Entry('auth/w/token', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_audit_hist = privatePostAuthRAuditHist = Entry('auth/r/audit/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_transfer = privatePostAuthWTransfer = Entry('auth/w/transfer', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_deposit_address = privatePostAuthWDepositAddress = Entry('auth/w/deposit/address', 'private', 'POST', {'cost': 24})
    private_post_auth_w_deposit_invoice = privatePostAuthWDepositInvoice = Entry('auth/w/deposit/invoice', 'private', 'POST', {'cost': 24})
    private_post_auth_w_withdraw = privatePostAuthWWithdraw = Entry('auth/w/withdraw', 'private', 'POST', {'cost': 24})
    private_post_auth_r_movements_currency_hist = privatePostAuthRMovementsCurrencyHist = Entry('auth/r/movements/{currency}/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_movements_hist = privatePostAuthRMovementsHist = Entry('auth/r/movements/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_alerts = privatePostAuthRAlerts = Entry('auth/r/alerts', 'private', 'POST', {'cost': 5.34})
    private_post_auth_w_alert_set = privatePostAuthWAlertSet = Entry('auth/w/alert/set', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_alert_price_symbol_price_del = privatePostAuthWAlertPriceSymbolPriceDel = Entry('auth/w/alert/price:{symbol}:{price}/del', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_alert_type_symbol_price_del = privatePostAuthWAlertTypeSymbolPriceDel = Entry('auth/w/alert/{type}:{symbol}:{price}/del', 'private', 'POST', {'cost': 2.7})
    private_post_auth_calc_order_avail = privatePostAuthCalcOrderAvail = Entry('auth/calc/order/avail', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_settings_set = privatePostAuthWSettingsSet = Entry('auth/w/settings/set', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_settings = privatePostAuthRSettings = Entry('auth/r/settings', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_settings_del = privatePostAuthWSettingsDel = Entry('auth/w/settings/del', 'private', 'POST', {'cost': 2.7})
    private_post_auth_r_pulse_hist = privatePostAuthRPulseHist = Entry('auth/r/pulse/hist', 'private', 'POST', {'cost': 2.7})
    private_post_auth_w_pulse_add = privatePostAuthWPulseAdd = Entry('auth/w/pulse/add', 'private', 'POST', {'cost': 16})
    private_post_auth_w_pulse_del = privatePostAuthWPulseDel = Entry('auth/w/pulse/del', 'private', 'POST', {'cost': 2.7})
