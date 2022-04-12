import datetime
import json

import requests
from django.core.cache import cache
from django.db import models

from trade.currencies import ALL_CURRENCIES
from user.models import Account


class Nobitex(Account):
    token = models.CharField(max_length=100)

    @staticmethod
    def get_currency_symbol(currency):
        if currency == 'IRR':
            return 'rls'
        else:
            return currency.lower()

    @staticmethod
    def get_raw_orderbook(market_symbol, is_bids):
        cache_key = 'nobitex_orderbook'
        response = cache.get(cache_key)
        order_book_type = 'asks'
        if is_bids:
            order_book_type = 'bids'
        return response[market_symbol][order_book_type]

    @staticmethod
    def get_raw_trades(market_symbol, is_sell):
        cache_key = 'nobitex_trades_' + market_symbol
        all_trades = cache.get(cache_key)
        trade_type = 'buy'
        if is_sell:
            trade_type = 'sell'
        specific_type_trades = []
        for trade in all_trades:
            if trade['type'] == trade_type:
                specific_type_trades.append(trade)
        return specific_type_trades

    @staticmethod
    def get_toman_price_from_raw_order(raw_order):
        return int(raw_order[0])

    @staticmethod
    def get_size_from_raw_order(raw_order):
        return float(raw_order[1])

    @staticmethod
    def get_toman_price_from_raw_trade(raw_trade):
        return int(raw_trade['price'])

    @staticmethod
    def get_size_from_raw_trade(raw_trade):
        return float(raw_trade['volume'])

    @staticmethod
    def get_time_from_raw_trade(raw_trade):
        return datetime.datetime.utcfromtimestamp(int(raw_trade['time']))

    def has_authentication_information(self):
        url = "https://api.nobitex.ir/users/profile"
        headers = {
            'Authorization': 'Token ' + self.token,
        }
        response = requests.get(url, headers=headers).json()
        try:
            return response['status'] == 'ok'
        except KeyError:
            return False

    def get_authentication_headers(self):
        if not self.has_authentication_information():
            self.raise_authentication_expired_exception()
        header = {
            'Authorization': 'Token ' + self.token,
        }
        return header

    def new_order(self, source, dest, amount, price, is_sell):
        side = 'sell' if is_sell else 'buy'
        data = json.dumps({
            "type": side,
            "srcCurrency": self.get_currency_symbol(source),
            "dstCurrency": self.get_currency_symbol(dest),
            "amount": float(amount),
            "price": int(price)})
        headers = self.get_authentication_headers().update({
            'content-type': 'application/json',
        })
        url = "https://api.nobitex.ir/market/orders/add"
        response = requests.post(url, headers=headers, data=data)
        response = response.json()
        if response['status'] == 'ok':
            return str(response['order']['id'])
        return ""

    def get_balance(self, currency):
        cache_key = 'nobitex_balance_' + currency + '_' + str(self.id)
        if cache_key not in cache:
            data = json.dumps({"currency": self.get_currency_symbol(currency)})
            url = "https://api.nobitex.ir/users/wallets/balance"
            response = requests.post(url, headers=self.get_authentication_headers(), data=data)
            response = response.json()
            cache.set(cache_key, response, timeout=300)
        else:
            response = cache.get(cache_key)
        if response['status'] == 'ok':
            return float(response['balance'])
        return ""

    def get_balance_of_all_currencies(self):
        balance_of_all = []
        for currency_tuple in ALL_CURRENCIES:
            currency = currency_tuple[0]
            balance = self.get_balance(currency)
            if balance > 0.0:
                balance_of_all.append((currency, balance))
        return balance_of_all

    @classmethod
    def get_market_info(cls, source, dest):
        source = cls.get_currency_symbol(source)
        dest = cls.get_currency_symbol(dest)
        cache_key = 'nobitex_market_' + source + '_' + dest
        response = cache.get(cache_key)
        response = response['stats'][source + '-' + dest]
        return {
            'bestSell': round(float(response['bestSell'])),
            'bestBuy': round(float(response['bestBuy'])),
        }
