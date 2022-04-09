import datetime
import json

import requests
from django.db import models
from django.utils import timezone

from user.models import Account


class Wallex(Account):
    token = models.CharField(max_length=100)
    token_expire_time = models.DateTimeField()

    def get_token(self, email, password):
        pass  # throw user

    @staticmethod
    def get_toman_symbol():
        return 'TMN'

    @staticmethod
    def get_currency_symbol(currency):
        if currency == 'IRR':
            return 'TMN'
        else:
            return currency

    @staticmethod
    def get_raw_orderbook(market_symbol, is_bids):
        url = "https://api.wallex.ir/v1/depth?symbol=" + market_symbol
        response = requests.get(url)
        order_book_type = 'ask'
        if is_bids:
            order_book_type = 'bid'
        return response.json()[order_book_type]

    @staticmethod
    def get_raw_trades(market_symbol, is_sell):
        url = "https://api.wallex.ir/v1/trades?symbol=" + market_symbol
        response = requests.get(url)
        all_trades = response.json()['latestTrades']
        specific_type_trades = []
        for trade in all_trades:
            if trade['isBuyOrder'] != is_sell:
                specific_type_trades.append(trade)
        return specific_type_trades

    @staticmethod
    def get_toman_price_from_raw_order(raw_order):
        return int(raw_order['price'])

    @staticmethod
    def get_size_from_raw_order(raw_order):
        return float(raw_order['quantity'])

    @staticmethod
    def get_toman_price_from_raw_trade(raw_trade):
        return int(raw_trade['price'])

    @staticmethod
    def get_size_from_raw_trade(raw_trade):
        return float(raw_trade['quantity'])

    @staticmethod
    def get_time_from_raw_trade(raw_trade):
        zulu_time = raw_trade['timestamp']
        return datetime.datetime.strptime(zulu_time, '%Y-%m-%dT%H:%M:%S.%fZ')

    def has_authentication_information(self):
        return self.token_expire_time > timezone.now()

    def get_authentication_headers(self):
        if not self.has_authentication_information():
            self.raise_authentication_expired_exception()
        header = {
            'Authorization': 'Bearer ' + self.token,
        }
        return header

    def new_order(self, source, dest, amount, price, is_sell):
        side = 'sell' if is_sell else 'buy'
        market_symbol = self.get_market_symbol(source, dest)
        if source == 'IRR':
            price = price / 10
        data = json.dumps({
            "price": str(price),
            "quantity": str(amount),
            "side": side,
            "symbol": market_symbol,
            "type": "limit",
        })
        headers = self.get_authentication_headers().update({
            'Content-Type': 'application/json',
        })
        url = "https://api.wallex.ir/v1/account/orders"
        response = requests.post(url, headers=headers, data=data)
        response = response.json()
        if response['success']:
            return response['result']['clientOrderId']
        return ""

    def get_balance(self, currency):
        url = "https://api.wallex.ir/v1/account/balances"
        response = requests.get(url, headers=self.get_authentication_headers(), data="")
        response = response.json()
        if response['success']:
            response = response['result']['balances'][self.get_currency_symbol(currency)]
            total = float(response['value'])
            locked = float(response['locked'])
            balance = total - locked
            if currency == 'IRR':
                balance = balance * 10
            return balance
        return ""
