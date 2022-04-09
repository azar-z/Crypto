import datetime
import json

import requests
from django.db import models
from django.utils import timezone

from user.models import Account


class Nobitex(Account):
    token = models.CharField(max_length=100)
    email = models.EmailField()
    token_expire_time = models.DateTimeField()

    @staticmethod
    def get_currency_symbol(currency):
        if currency == 'IRR':
            return 'rls'
        else:
            return currency.lower()

    def get_token(self, email, password):
        pass  # throw login, set expire date

    @staticmethod
    def get_raw_orderbook(market_symbol, is_bids):
        url = 'https://api.nobitex.ir/v2/orderbook/' + market_symbol
        response = requests.get(url)
        order_book_type = 'asks'
        if is_bids:
            order_book_type = 'bids'
        return response.json()[order_book_type]

    @staticmethod
    def get_raw_trades(market_symbol, is_sell):
        url = 'https://api.nobitex.ir/v2/trades/' + market_symbol
        response = requests.get(url)
        all_trades = response.json()['trades']
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
        return int(raw_order[1])

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
        data = json.dumps({
            "type": side,
            "srcCurrency": self.get_currency_symbol(source),
            "dstCurrency": self.get_currency_symbol(dest),
            "amount": float(amount),
            "price": int(price)})
        headers = self.get_authentication_headers().update({
            'Content-Type': 'application/json',
        })
        url = "https://api.nobitex.ir/market/orders/add"
        response = requests.post(url, headers=headers, data=data)
        response = response.json()
        if response['status'] == 'ok':
            return str(response['order']['id'])
        return ""

    def get_balance(self, currency):
        data = json.dumps({"currency": self.get_currency_symbol(currency)})
        url = "https://api.nobitex.ir/users/wallets/balance"
        response = requests.post(url, headers=self.get_authentication_headers(), data=data)
        response = response.json()
        if response['status'] == 'ok':
            return float(response['balance'])
        return ""
