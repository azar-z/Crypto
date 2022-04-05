import datetime

import requests
from django.db import models

from user.models import Account


class Exir(Account):
    api_key = models.CharField(max_length=200)
    api_signature = models.CharField(max_length=200)
    api_expires = models.CharField(max_length=200)

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

    def new_order(self, source, dest, amount, price, is_sell):
        pass