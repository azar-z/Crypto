import datetime

import requests
from django.db import models

from user.models import Account


class Wallex(Account):
    token = models.CharField(max_length=100)
    token_expire_time = models.DateTimeField()

    def get_token(self, email, password):
        pass  # throw user

    # WebSocket?

    @staticmethod
    def get_toman_symbol():
        return 'TMN'

    @staticmethod
    def get_raw_orderbook(source, dest, is_bids):
        if dest == "IRR":
            dest = Wallex.get_toman_symbol()
        url = "https://api.wallex.ir/v1/depth?symbol=" + source + dest
        response = requests.get(url)
        order_book_type = 'ask'
        if is_bids:
            order_book_type = 'bid'
        return response.json()[order_book_type]

    @staticmethod
    def get_raw_trades(source, dest, is_sell):
        if dest == "IRR":
            dest = Wallex.get_toman_symbol()
        url = "https://api.wallex.ir/v1/trades?symbol=" + source + dest
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
