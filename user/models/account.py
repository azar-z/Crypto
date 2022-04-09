from django.db import models
from django.utils import timezone

import user.validators.account as validators
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
    _was_default = False
    is_default = models.BooleanField(default=False)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, validators=[validators.validate_not_staff],
                                 related_name='%(class)s_account')
    type = models.CharField(max_length=1, choices=ACCOUNT_TYPE_CHOICES)

    def save(self, *args, **kwargs):
        if self.is_default and not self._was_default:
            self.set_as_default()
            self._was_default = True
        if not self.is_default and self._was_default:
            self._was_default = False
        super(Account, self).save(*args, **kwargs)

    @staticmethod
    def get_toman_symbol():
        return 'IRT'

    @staticmethod
    def get_currency_symbol(currency):
        pass

    @classmethod
    def get_market_symbol(cls, source, dest):
        if source == 'IRR':
            source = cls.get_toman_symbol()
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
        orders.sort(reverse=True)
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
            time = cls.get_time_from_raw_trade(raw_trade)
            market = cls.__name__
            trades.append({"price": price, "size": size, "time": time, "market": market})
        return trades

    @staticmethod
    def get_trades_of_all(market_symbol, is_sell):
        trades = []
        for subclass in Account.__subclasses__():
            trades.extend(subclass.get_trades(market_symbol, is_sell))
        trades.sort(reverse=True)
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

    def set_as_default(self):
        account = self.owner.nobitex_account
        if account is not self:
            account.is_default = False
            account._was_default = False
            account.save()
        account = self.owner.wallex_account
        if account is not self:
            account.is_default = False
            account._was_default = False
            account.save()
        account = self.owner.exir_account
        if account is not self:
            account.is_default = False
            account._was_default = False
            account.save()
        self.is_default = True

    @staticmethod
    def raise_authentication_expired_exception():
        raise Exception('No authentication information.')

    def get_authentication_headers(self):
        pass

    def new_order(self, source, dest, amount, price, is_sell):
        pass

    def get_balance(self, currency):
        pass

    def has_authentication_information(self):
        pass

    def get_wallets(self):
        pass
        # usage??

    class Meta:
        abstract = True
