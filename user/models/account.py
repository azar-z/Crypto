from operator import itemgetter

from django.db import models
from django.utils import timezone

import user.validators.account as validators
from trade.currencies import SOURCE_CURRENCIES
from user.errors import NoAuthenticationInformation
from user.models.base_model import BaseModel
from user.models.user import User

ACCOUNT_TYPE_CHOICES = (
    ('N', "Nobitex"),
    ('W', "Wallex"),
    ('E', "Exir"),
)

NUMBER_OF_ROWS = 6

# source = BTC
# dest = IRR


class Account(BaseModel):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, validators=[validators.validate_not_staff],
                                 related_name='%(class)s_account')
    needs_withdraw_confirmation = models.BooleanField(default=False)

    @staticmethod
    def is_orderbook_in_toman():
        return True

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
        raw_orders = cls.get_raw_orderbook(market_symbol, is_bids)[:NUMBER_OF_ROWS]
        orders = []
        for raw_order in raw_orders:
            price = round(cls.get_price_from_raw_order(raw_order), 2)
            size = round(cls.get_size_from_raw_order(raw_order), 6)
            total = round(float(price) * size, 2)
            market = cls.__name__
            orders.append({"price": price, "size": size, "total": total, "market": market})
        orders = sorted(orders, key=itemgetter('price'), reverse=True)
        if is_bids:
            return orders[-NUMBER_OF_ROWS:]
        return orders[:NUMBER_OF_ROWS]

    @staticmethod
    def get_orderbook_of_all(source, dest, is_bids):
        orders = []
        for subclass in Account.__subclasses__():
            market_symbol = subclass.get_market_symbol(source, dest)
            orders.extend(subclass.get_orderbook(market_symbol, is_bids))
        orders = sorted(orders, key=itemgetter('price'), reverse=True)
        if is_bids:
            return orders[-NUMBER_OF_ROWS:]
        return orders[:NUMBER_OF_ROWS]

    @staticmethod
    def get_price_from_raw_order(raw_order):
        return 0

    @staticmethod
    def get_size_from_raw_order(raw_order):
        return 0

    @classmethod
    def get_trades(cls, market_symbol, is_sell):
        raw_trades = cls.get_raw_trades(market_symbol, is_sell)[:NUMBER_OF_ROWS]
        trades = []
        for raw_trade in raw_trades:
            price = round(cls.get_price_from_raw_trade(raw_trade), 2)
            size = round(cls.get_size_from_raw_trade(raw_trade), 6)
            total = round(float(price) * size, 2)
            market = cls.__name__
            trades.append({"price": price, "size": size, "total": total, "market": market})
        trades = sorted(trades, key=itemgetter('price'), reverse=True)
        if is_sell:
            return trades[-NUMBER_OF_ROWS:]
        return trades[:NUMBER_OF_ROWS]

    @staticmethod
    def get_trades_of_all(source, dest, is_sell):
        trades = []
        for subclass in Account.__subclasses__():
            market_symbol = subclass.get_market_symbol(source, dest)
            trades.extend(subclass.get_trades(market_symbol, is_sell))
        trades = sorted(trades, key=itemgetter('price'), reverse=True)
        if is_sell:
            return trades[-NUMBER_OF_ROWS:]
        return trades[:NUMBER_OF_ROWS]

    @staticmethod
    def get_raw_trades(market_symbol, is_sell):
        pass

    @staticmethod
    def get_price_from_raw_trade(raw_trade):
        return 0

    @staticmethod
    def get_size_from_raw_trade(raw_trade):
        return 0

    @staticmethod
    def get_time_from_raw_trade(raw_trade):
        return timezone.now()

    @classmethod
    def get_market_info(cls, source, dest):
        pass

    @staticmethod
    def get_market_info_of_all(dest):
        market_info = []
        for currency_tuple in SOURCE_CURRENCIES:
            currency = currency_tuple[0]
            _market_info = {}
            for subclass in Account.__subclasses__():
                subclass_market_info = subclass.get_market_info(currency, dest)
                _market_info.update({
                    subclass.__name__.lower(): subclass_market_info
                })
            market_info.append({'currency': currency, 'info': _market_info})
        return market_info

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

    def request_withdraw(self, currency, amount, address):
        return False

    def confirm_withdraw(self, withdraw_id, otp):
        return False

    @classmethod
    def make_an_account_for_user(cls, user):
        account = cls.objects.create(owner=user)
        account.save()
        return account

    def get_order_status(self, order_id):
        pass

    class Meta:
        abstract = True
