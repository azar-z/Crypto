from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from trade.currencies import SOURCE_CURRENCIES, DEST_CURRENCIES, AccountOrderStatus
from user.logics.accounts import get_account_based_on_type
from user.models import BaseModel, User
from user.models.account import ACCOUNT_TYPE_CHOICES

ORDER_STATUS_CHOICES = (
    ('NO', 'this phase of order hasn\'t started yet'),
    ('OS', 'transaction step was ordered successfully'),
    ('OU', 'transaction was ordered unsuccessfully'),
    ('OD', 'transaction is done'),
    ('L', 'got to loss or profit limit (second step not started yet)'),
    ('TOS', 'transfer ordered successfully'),
    ('TOU', 'transfer ordered unsuccessfully'),
    ('TD', 'transfer done'),
)
'''
possible ways:
1. FOU
2. FOS -> FD  (has_second_step = False)
3. FOS -> FD -> L -> MD -> SOU  (has_second_step = True & needs_moving() = False)
4. FOS -> FD -> L -> MD -> SOS -> SOD  (has_second_step = True & needs_moving() = False)
5. FOS -> FD -> L -> TOU  (has_second_step = True & needs_moving() = True)
6. FOS -> FD -> L -> TOS -> MD -> SOU  (has_second_step = True & needs_moving() = True)
7. FOS -> FD -> L -> TOS -> MD -> SOS -> SD  (has_second_step = True & needs_moving() = True)
'''


# source = BTC
# dest = IRR


class Order(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True)
    status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=3, default='NO')
    time = models.DateTimeField(default=timezone.now)
    is_sell = models.BooleanField(null=False)
    price = models.IntegerField()
    account_type = models.CharField(choices=ACCOUNT_TYPE_CHOICES, max_length=2)
    id_in_account = models.CharField(default='0', max_length=100)
    source_currency_type = models.CharField(verbose_name='First Currency', max_length=4, choices=SOURCE_CURRENCIES)
    dest_currency_type = models.CharField(verbose_name='Second Currency', max_length=4, choices=DEST_CURRENCIES)
    source_currency_amount = models.DecimalField(verbose_name='First Currency Amount', max_digits=15, decimal_places=5)
    profit_limit = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                     blank=True)
    got_to_profit_limit = models.BooleanField(default=False)
    loss_limit = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], blank=True)
    got_to_loss_limit = models.BooleanField(default=False)
    deposit_wallet_address = models.CharField(max_length=200, null=True, default=None, blank=True)
    withdraw_id = models.CharField(max_length=200, null=True, default=None)
    transfer_fee = models.DecimalField(max_digits=15, decimal_places=5, default=0.0)
    next_step = models.OneToOneField('self', null=True, blank=True, on_delete=models.SET_NULL, default=None,
                                     related_name='previous_step')

    class Meta:
        ordering = ('-updated',)

    def has_next_step(self):
        return self.next_step is not None

    def get_profit_limit_price(self):
        return self.price * (1 + self.profit_limit)

    def get_loss_limit_price(self):
        return self.price * (1 - self.loss_limit)

    def needs_transfer(self):
        return self.account_type != self.next_step.account_type

    def get_account(self):
        return get_account_based_on_type(self.owner, self.account_type)

    def get_next_step_account(self):
        return get_account_based_on_type(self.owner, self.next_step.account_type)

    def order_transaction(self):
        self.time = timezone.now()
        account = self.get_account()
        id_in_account = account.new_order(source=self.source_currency_type, dest=self.dest_currency_type,
                                          amount=self.source_currency_amount, price=self.price,
                                          is_sell=self.is_sell)
        if id_in_account:
            self.id_in_account = id_in_account
            self.status = 'OS'
        else:
            self.status = 'OU'
        self.save()

    def check_for_order_status(self):
        account = self.get_account()
        account_order_status = account.get_order_status(self.id_in_account)
        self.status = self.get_status_based_on_account_order_status(account_order_status)
        self.save()

    @staticmethod
    def get_status_based_on_account_order_status(account_order_status):
        if account_order_status == AccountOrderStatus.DONE:
            status = 'OD'
        elif account_order_status == AccountOrderStatus.CANCELLED:
            status = 'OU'
        else:
            status = 'OS'
        return status

    def check_for_profit_or_loss_limits(self):
        account = self.get_next_step_account()
        market_info = account.get_market_info(self.source_currency_type, self.dest_currency_type)
        market_lowest_price = market_info['bestBuy']
        market_highest_price = market_info['bestSell']
        if market_highest_price <= self.get_loss_limit_price():
            self.got_to_loss_limit = True
            self.second_step_price = market_highest_price
            self.status = 'L'
        elif market_lowest_price >= self.get_profit_limit_price():
            self.got_to_profit_limit = True
            self.second_step_price = market_highest_price
            self.status = 'L'
        self.save()
        if self.status == 'L':
            return True
        return False

    def check_for_enough_balance(self):
        account = self.get_account()
        if self.is_sell:
            balance = account.get_balance(self.source_currency_type)
            amount = self.source_currency_amount
        else:
            balance = account.get_balance(self.dest_currency_type)
            amount = self.get_total()
        if balance >= amount and self.status == 'TOS':
            return True
        return False

    def get_profit_or_loss(self):
        return self.source_currency_amount * (self.second_step_price - self.price)

    def get_total(self):
        return round(self.source_currency_amount * self.price, 2)
