from django.core.cache import cache
from django.test import TestCase

from trade.tests.utils import create_user, make_user_authenticated
from user.models import Nobitex


class NobitexModelTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.account = self.user.nobitex_account

    def test_get_market_symbol(self):
        source = 'BTC'
        dest = 'USDT'
        self.assertEqual(Nobitex.get_market_symbol(source, dest), 'BTCUSDT')

    def test_get_currency_symbol(self):
        currency = 'BTC'
        self.assertEqual(Nobitex.get_currency_symbol(currency), 'btc')

    def test_get_raw_orderbook(self):
        bids_list = [["39186.98", "0.001413"], ["39187", "0.003459"]]
        asks_list = [["38920", "0.047"], ["38900", "0.005141"]]
        market_symbol = 'BTCUSDT'
        order_book = {"status": "ok",
                      market_symbol: {"lastUpdate": 1644991756704, "bids": bids_list, "asks": asks_list}}
        cache_key = 'nobitex_orderbook'
        cache.set(cache_key, order_book)
        self.assertEqual(Nobitex.get_raw_orderbook(market_symbol, True), bids_list)
        self.assertEqual(Nobitex.get_raw_orderbook(market_symbol, False), asks_list)

    def test_get_raw_trades(self):
        trade_sell = {"time": 1651098999079, "price": "39051", "volume": "0.000695", "type": "sell"}
        trade_buy = {"time": 1651097975805, "price": "49904", "volume": "0.0089", "type": "buy"}
        all_trades = [trade_sell, trade_buy]
        market_symbol = 'BTCUSDT'
        cache_key = 'nobitex_trades_' + market_symbol
        cache.set(cache_key, all_trades)
        self.assertListEqual(Nobitex.get_raw_trades(market_symbol, True), [trade_sell])
        self.assertListEqual(Nobitex.get_raw_trades(market_symbol, False), [trade_buy])

    def test_get_data_from_raw_order(self):
        price = 39186.98
        size = 0.001413
        order = [str(price), str(size)]
        self.assertEqual(Nobitex.get_price_from_raw_order(order), price)
        self.assertEqual(Nobitex.get_size_from_raw_order(order), size)

    def test_get_data_from_raw_trade(self):
        price = 39051
        size = 0.000695
        trade = {"time": 1651098999079, "price": str(price), "volume": str(size), "type": "sell"}
        self.assertEqual(Nobitex.get_price_from_raw_trade(trade), 39051)
        self.assertEqual(Nobitex.get_size_from_raw_trade(trade), 0.000695)

    def test_has_authentication_information(self):
        account = self.account
        self.assertFalse(account.has_authentication_information())
        make_user_authenticated(self.user)
        self.assertTrue(account.has_authentication_information())



'''
    def new_order(self, source, dest, amount, price, is_sell):
    
    def get_balance(self, currency):

    def get_balance_of_all_currencies(self):

    @classmethod
    def get_market_info(cls, source, dest):

    def get_wallet_id(self, currency):

    def _request_withdraw(self, wallet, amount, address):

    def confirm_withdraw(self, withdraw_id, otp):

    def get_order_status(self, order_id):
'''
