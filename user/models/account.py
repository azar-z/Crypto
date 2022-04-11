from operator import itemgetter

from django.db import models
from django.utils import timezone

import user.validators.account as validators
from user.errors import NoAuthenticationInformation
from user.models.base_model import BaseModel
from user.models.user import User

ACCOUNT_TYPE_CHOICES = (
    ('N', "Nobitex"),
    ('W', "Wallex"),
    ('E', "Exir"),
)


# source = BTC
# dest = IRR


class Account(BaseModel):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, validators=[validators.validate_not_staff],
                                 related_name='%(class)s_account')

    @staticmethod
    def get_toman_symbol():
        return 'IRT'

    @staticmethod
    def get_currency_symbol(currency):
        pass

    @classmethod
    def get_market_symbol(cls, source, dest):
        if dest == 'IRR':
            dest = cls.get_toman_symbol()
        return source + dest

    @staticmethod
    def get_raw_orderbook(market_symbol, is_sell):
        pass

    @classmethod
    def get_orderbook(cls, market_symbol, is_bids):
        raw_orders = cls.get_raw_orderbook(market_symbol, is_bids)[:10]
        orders = []
        for raw_order in raw_orders:
            price = cls.get_toman_price_from_raw_order(raw_order)
            if cls.get_toman_symbol() in market_symbol:
                price *= 10
            size = cls.get_size_from_raw_order(raw_order)
            total = price * size
            market = cls.__name__
            orders.append({"price": price, "size": size, "total": total, "market": market})
        return orders

    @staticmethod
    def get_orderbook_of_all(source, dest, is_bids):
        orders = []
        for subclass in Account.__subclasses__():
            market_symbol = subclass.get_market_symbol(source, dest)
            orders.extend(subclass.get_orderbook(market_symbol, is_bids))
        orders = sorted(orders, key=itemgetter('price'), reverse=True)
        return orders[:10]

    @staticmethod
    def get_toman_price_from_raw_order(raw_order):
        return 0

    @staticmethod
    def get_size_from_raw_order(raw_order):
        return 0

    @classmethod
    def get_trades(cls, market_symbol, is_sell):
        raw_trades = cls.get_raw_trades(market_symbol, is_sell)[:10]
        trades = []
        for raw_trade in raw_trades:
            price = cls.get_toman_price_from_raw_trade(raw_trade)
            if cls.get_toman_symbol() in market_symbol:
                price *= 10
            size = cls.get_size_from_raw_trade(raw_trade)
            # time = cls.get_time_from_raw_trade(raw_trade)
            market = cls.__name__
            trades.append({"price": price, "size": size, "time": 'some time', "market": market})
        return trades

    @staticmethod
    def get_trades_of_all(source, dest, is_sell):
        trades = []
        for subclass in Account.__subclasses__():
            market_symbol = subclass.get_market_symbol(source, dest)
            trades.extend(subclass.get_trades(market_symbol, is_sell))
        trades = sorted(trades, key=itemgetter('price'), reverse=True)
        return trades[:10]

    @staticmethod
    def get_raw_trades(market_symbol, is_sell):
        pass

    @staticmethod
    def get_toman_price_from_raw_trade(raw_trade):
        return 0

    @staticmethod
    def get_size_from_raw_trade(raw_trade):
        return 0

    @staticmethod
    def get_time_from_raw_trade(raw_trade):
        return timezone.now()

    @staticmethod
    def raise_authentication_expired_exception():
        raise NoAuthenticationInformation('No authentication information.')

    def get_authentication_headers(self):
        pass

    def new_order(self, source, dest, amount, price, is_sell):
        pass

    def get_balance(self, currency):
        pass

    def get_balance_of_all_currencies(self):
        pass

    def has_authentication_information(self):
        pass

    def get_wallets(self):
        pass
        # usage??

    class Meta:
        abstract = True
