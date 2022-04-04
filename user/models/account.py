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


class Account(BaseModel):
    _was_default = False
    is_default = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, validators=[validators.validate_not_staff])
    type = models.CharField(max_length=1, choices=ACCOUNT_TYPE_CHOICES)

    def save(self, *args, **kwargs):
        if self.is_default and not self._was_default:
            self.set_as_default()
            self._was_default = True
        if not self.is_default and self._was_default:
            self._was_default = False
        super(Account, self).save(*args, **kwargs)

    @staticmethod
    def get_raw_orderbook(source, dest, is_bids):
        pass

    @staticmethod
    def get_toman_symbol():
        return 'IRT'

    @classmethod
    def get_orderbook(cls, source, dest, is_bids):
        raw_orders = cls.get_raw_orderbook(source, dest, is_bids)[:10]
        orders = []
        for raw_order in raw_orders:
            price = cls.get_toman_price_from_raw_order(raw_order)
            if dest == "IRR":
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
            orders.extend(subclass.get_orderbook(source, dest, is_bids))
        orders.sort(reverse=True)
        return orders[:10]

    @staticmethod
    def get_toman_price_from_raw_order(raw_order):
        return 0

    @staticmethod
    def get_size_from_raw_order(raw_order):
        return 0

    @classmethod
    def get_trades(cls, source, dest, is_sell):
        raw_trades = cls.get_raw_trades(source, dest, is_sell)[:10]
        trades = []
        for raw_trade in raw_trades:
            price = cls.get_toman_price_from_raw_trade(raw_trade)
            if dest == "IRR":
                price *= 10
            size = cls.get_size_from_raw_trade(raw_trade)
            time = cls.get_time_from_raw_trade(raw_trade)
            market = cls.__name__
            trades.append({"price": price, "size": size, "time": time, "market": market})
        return trades

    @staticmethod
    def get_trades_of_all(source, dest, is_sell):
        trades = []
        for subclass in Account.__subclasses__():
            trades.extend(subclass.get_trades(source, dest, is_sell))
        trades.sort(reverse=True)
        return trades[:10]

    @staticmethod
    def get_raw_trades(source, dest, is_sell):
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
        for account in self.owner.account_set.all():
            if account is not self:
                account.is_default = False
                account._was_default = False
                account.save()
        self.is_default = True

    def new_order(self, source, dest, amount, price):
        pass

    def cancel_order(self, order):
        pass

    def get_inventory(self, currency):
        pass

    def logout(self):
        pass

    def has_authentication_information(self):
        pass
        # boolean output

    def get_authentication_information(self):
        pass

    def get_wallets(self):
        pass


