import datetime

import requests
from django.db import models

from user.models import Account


class Exir(Account):
    api_key = models.CharField(max_length=200)
    api_signature = models.CharField(max_length=200)
    api_expires = models.CharField(max_length=200)

    @staticmethod
    def get_raw_orderbook(source, dest, is_bids):
        if dest == "IRR":
            dest = Exir.get_toman_symbol()
        source = source.lower()
        dest = dest.lower()
        url = "https://api.exir.io/v1/orderbooks"
        response = requests.get(url)
        market_name = source + "-" + dest
        order_book_type = 'asks'
        if is_bids:
            order_book_type = 'bids'
        return response.json()[market_name][order_book_type]

    @staticmethod
    def get_raw_trades(source, dest, is_sell):
        if dest == "IRR":
            dest = Exir.get_toman_symbol()
        source = source.lower()
        dest = dest.lower()
        url = "https://api.exir.io/v1/trades"
        response = requests.get(url)
        market_name = source + "-" + dest
        all_trades = response.json()[market_name]
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
