import datetime
import json

import requests
from django.db import models

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

    def new_order(self, source, dest, amount, price, is_sell):
        side = 'sell' if is_sell else 'buy'
        market_symbol = self.get_market_symbol(source, dest)
        payload = json.dumps({
            "price": str(price),
            "quantity": str(amount),
            "side": "sell",
            "symbol": self.get_market_symbol(source, dest),
            "type": "market",
        })
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }
        url = "https://api.wallex.ir/v1/account/orders"
        response = requests.post(url, headers=headers, data=payload)
        if response.json()['success']:
            return True
        return False
