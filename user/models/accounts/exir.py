import datetime
import json

import requests
from django.db import models
from django.utils import timezone

from user.models import Account


class Exir(Account):
    api_key = models.CharField(max_length=200)
    api_signature = models.CharField(max_length=200)
    api_expires = models.CharField(max_length=200)
    api_key_expire_time = models.DateTimeField()

    @staticmethod
    def get_currency_symbol(currency):
        if currency == 'IRR':
            return 'irt'
        else:
            return currency.lower()

    @classmethod
    def get_market_symbol(cls, source, dest):
        if source == 'IRR':
            source = cls.get_toman_symbol()
        source = source.lower()
        dest = dest.lower()
        return source + "-" + dest

    @classmethod
    def get_orderbook(cls, market_symbol, is_bids):
        url = "https://api.exir.io/v1/orderbooks"
        response = requests.get(url)
        order_book_type = 'asks'
        if is_bids:
            order_book_type = 'bids'
        return response.json()[market_symbol][order_book_type]

    @staticmethod
    def get_raw_trades(market_symbol, is_sell):
        url = "https://api.exir.io/v1/trades"
        response = requests.get(url)
        all_trades = response.json()[market_symbol]
        trade_type = 'buy'
        if is_sell:
            trade_type = 'sell'
        specific_type_trades = []
        for trade in all_trades:
            if trade['side'] == trade_type:
                specific_type_trades.append(trade)
        return specific_type_trades

    @staticmethod
    def get_toman_price_from_raw_order(raw_order):
        return int(raw_order[0])

    @staticmethod
    def get_size_from_raw_order(raw_order):
        return int(raw_order[1])

    @staticmethod
    def get_toman_price_from_raw_trade(raw_trade):
        return int(raw_trade['price'])

    @staticmethod
    def get_size_from_raw_trade(raw_trade):
        return float(raw_trade['size'])

    @staticmethod
    def get_time_from_raw_trade(raw_trade):
        zulu_time = raw_trade['timestamp']
        return datetime.datetime.strptime(zulu_time, '%Y-%m-%dT%H:%M:%S.%fZ')

    def has_authentication_information(self):
        return self.api_key_expire_time > timezone.now()

    def get_authentication_headers(self):
        if not self.has_authentication_information():
            self.raise_authentication_expired_exception()
        header = {
            'api-expires': self.api_expires,
            'api-signature': self.api_signature,
            'api-key': self.api_key,
        }
        return header

    def new_order(self, source, dest, amount, price, is_sell):
        side = 'sell' if is_sell else 'buy'
        market_symbol = self.get_market_symbol(source, dest)
        price = price / 10
        data = json.dumps({
            "symbol": market_symbol,
            "side": side,
            "size": str(amount),
            "type": "limit",
            "price": str(price)
        })
        url = "https://api.exir.io/v1/order"
        response = requests.post(url, headers=self.get_authentication_headers(), data=data)
        response = response.json()
        if response['status'] == 'pending':
            return str(response['id'])
        return ""

    def get_balance(self, currency):
        url = "https://api.exir.io/v1/user/balance"
        response = requests.get(url, headers=self.get_authentication_headers())
        response = response.json()
        symbol = self.get_currency_symbol(currency) + '_available'
        balance = float(response[symbol])
        if currency == 'IRR':
            balance = balance * 10
        return balance
