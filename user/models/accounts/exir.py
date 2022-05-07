import datetime
import json
from decimal import Decimal
from operator import itemgetter

import requests
from django.core.cache import cache
from django.db import models

from trade.utils import ALL_CURRENCIES, AccountOrderStatus
from user.models import Account


class Exir(Account):
    api_key = models.CharField(max_length=200, blank=True)
    api_signature = models.CharField(max_length=200, blank=True)
    api_expires = models.CharField(max_length=200, blank=True)

    @staticmethod
    def get_currency_symbol(currency):
        if currency == 'IRR':
            return 'irt'
        else:
            return currency.lower()

    @classmethod
    def get_market_symbol(cls, source, dest):
        source = source.lower()
        dest = dest.lower()
        return source + "-" + dest

    @classmethod
    def get_raw_orderbook(cls, market_symbol, is_bids):
        cache_key = 'exir_orderbook'
        response = cache.get(cache_key)
        order_book_type = 'asks'
        if is_bids:
            order_book_type = 'bids'
        return response[market_symbol][order_book_type]

    @staticmethod
    def get_raw_trades(market_symbol, is_sell):
        cache_key = 'exir_tasks'
        response = cache.get(cache_key)
        all_trades = response[market_symbol]
        trade_type = 'buy'
        if is_sell:
            trade_type = 'sell'
        specific_type_trades = []
        for trade in all_trades:
            if trade['side'] == trade_type:
                specific_type_trades.append(trade)
        return specific_type_trades

    @staticmethod
    def get_price_from_raw_order(raw_order):
        return Decimal(raw_order[0])

    @staticmethod
    def get_size_from_raw_order(raw_order):
        return float(raw_order[1])

    @staticmethod
    def get_price_from_raw_trade(raw_trade):
        return Decimal(raw_trade['price'])

    @staticmethod
    def get_size_from_raw_trade(raw_trade):
        return float(raw_trade['size'])

    @staticmethod
    def get_time_from_raw_trade(raw_trade):
        zulu_time = raw_trade['timestamp']
        return datetime.datetime.strptime(zulu_time, '%Y-%m-%dT%H:%M:%S.%fZ')

    def has_authentication_information(self):
        url = "https://api.exir.io/v1/user"
        headers = {
            'api-expires': self.api_expires,
            'api-signature': self.api_signature,
            'api-key': self.api_key,
        }
        response = requests.get(url, headers=headers).json()
        try:
            return response['id'] != ""
        except KeyError:
            return False

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

    def get_balance_of_all_currencies(self):
        cache_key = 'exir_balance_' + str(self.id)
        if cache_key not in cache:
            url = "https://api.exir.io/v1/user/balance"
            response = requests.get(url, headers=self.get_authentication_headers())
            response = response.json()
            cache.set(cache_key, response, timeout=300)
        else:
            response = cache.get(cache_key)
        balance_of_all = []
        for currency_tuple in ALL_CURRENCIES:
            currency = currency_tuple[0]
            symbol = self.get_currency_symbol(currency) + '_available'
            balance = float(response[symbol])
            if currency == 'IRR':
                balance = balance * 10
            if balance > 0.0:
                balance_of_all.append((currency, balance))
        return balance_of_all

    @classmethod
    def get_market_info(cls, source, dest):
        sells = cls.get_trades(cls.get_market_symbol(source, dest), True)
        sells = sorted(sells, key=itemgetter('price'), reverse=True)
        buys = cls.get_trades(cls.get_market_symbol(source, dest), False)
        buys = sorted(buys, key=itemgetter('price'))
        best_sell = sells[0]
        best_buy = buys[0]
        return {
            'bestSell': round(float(best_sell['price']), 2),
            'bestBuy': round(float(best_buy['price']), 2),
        }

    def request_withdraw(self, currency, amount, address):
        url = "https://api.exir.io/v1/user/request-withdrawal"
        headers = self.get_authentication_headers()
        data = {
            "currency": self.get_currency_symbol(currency),
            "amount": str(amount),
            "address": address,
        }
        response = requests.get(url, headers=headers, data=data)
        response = response.json()
        try:
            return response['message'] == 'Success'
        except KeyError:
            return False

    def get_order_status(self, order_id):
        url = 'https://api.exir.io/v1/user/orders/' + order_id
        headers = self.get_authentication_headers()
        response = requests.get(url, headers=headers).json()
        try:
            size = response['size']
            filled = response['filled']
            if size < filled:
                return AccountOrderStatus.ACTIVE
            else:
                return AccountOrderStatus.DONE
        except KeyError:
            return AccountOrderStatus.CANCELLED

