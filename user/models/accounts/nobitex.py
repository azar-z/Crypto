import datetime

import requests
from django.db import models

from user.models import Account


class Nobitex(Account):
    token = models.CharField(max_length=100)
    email = models.EmailField()
    token_expire_time = models.DateTimeField()

    def get_token(self, email, password):
        pass  # throw login, set expire date

    @staticmethod
    def get_raw_orderbook(source, dest, is_bids):
        if dest == "IRR":
            dest = Nobitex.get_toman_symbol()
        url = 'https://api.nobitex.ir/v2/orderbook/' + source + dest
        response = requests.get(url)
        order_book_type = 'asks'
        if is_bids:
            order_book_type = 'bids'
        return response.json()[order_book_type]

    @staticmethod
    def get_raw_trades(source, dest, is_sell):
        if dest == "IRR":
            dest = Nobitex.get_toman_symbol()
        url = 'https://api.nobitex.ir/v2/trades/' + source + dest
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
