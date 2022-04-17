from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from trade.currencies import SOURCE_CURRENCIES, DEST_CURRENCIES, AccountOrderStatus
from user.logics.accounts import get_account_based_on_type
from user.models import BaseModel, User
from user.models.account import ACCOUNT_TYPE_CHOICES

ORDER_STATUS_CHOICES = (
    ('NO', 'Not started yet.'),
    ('OS', 'Transaction was ordered successfully but it is not done yet.'),
    ('OU', 'Transaction was not successful'),
    ('OD', 'Transaction is done.'),
    ('L', 'Got to limit. Check alerts to continue this order'),
    ('TOS', 'Transaction is done and transfer was ordered successfully but it is not done yet.'),
    ('TOU', 'Transaction is done but transfer was not successful'),
    ('TD', 'Transaction is done. Transfer is done.'),
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
    price = models.DecimalField(verbose_name='Price (USDT)', max_digits=20, decimal_places=2, default=0)
    account_type = models.CharField(verbose_name='In', choices=ACCOUNT_TYPE_CHOICES, max_length=2)
    id_in_account = models.CharField(default='0', max_length=100)
    source_currency_type = models.CharField(verbose_name='Currency', max_length=4, choices=SOURCE_CURRENCIES)
    dest_currency_type = models.CharField(max_length=4, choices=DEST_CURRENCIES, default='USDT')
    source_currency_amount = models.DecimalField(verbose_name='Amount', max_digits=15, decimal_places=5, default=0)
    profit_limit = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                     blank=True)
    loss_limit = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], blank=True)
    deposit_wallet_address = models.CharField(max_length=200, null=True, default=None, blank=True)
    withdraw_id = models.CharField(max_length=200, null=True, default=None)
    transfer_fee = models.DecimalField(max_digits=15, decimal_places=5, default=0.0)
    next_step = models.OneToOneField('self', null=True, blank=True, on_delete=models.SET_NULL, default=None,
                                     related_name='previous_step')

    class Meta:
        ordering = ('-updated',)

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})

    def has_next_step(self):
        return self.next_step is not None

    def get_profit_limit_price(self):
        if self.is_sell:
            return self.price / Decimal(1 + self.profit_limit)
        return self.price * Decimal(1 + self.profit_limit)

    def get_loss_limit_price(self):
        if self.is_sell:
            return self.price / Decimal(1 - self.loss_limit)
        return self.price * Decimal(1 - self.loss_limit)

    def needs_transfer(self):
        return self.has_next_step() and self.account_type != self.next_step.account_type

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
        if self.is_sell:
            if market_lowest_price >= self.get_loss_limit_price():
                self.next_step.price = market_highest_price
                self.next_step.source_currency_amount = self.source_currency_amount * Decimal(1 - self.loss_limit)
                self.status = 'L'
            elif market_highest_price <= self.get_profit_limit_price():
                self.next_step.price = market_highest_price
                self.next_step.source_currency_amount = self.source_currency_amount * Decimal(1 + self.profit_limit)
                self.status = 'L'
            self.save()
        else:
            if market_highest_price <= self.get_loss_limit_price():
                self.next_step.price = market_highest_price
                self.next_step.source_currency_amount = self.source_currency_amount
                self.status = 'L'
            elif market_lowest_price >= self.get_profit_limit_price():
                self.next_step.price = market_highest_price
                self.next_step.source_currency_amount = self.source_currency_amount
                self.status = 'L'
            self.save()
        if self.status == 'L':
            return True
        return False

    def got_to_profit_limit(self):
        return self.next_step.price > self.price

    def got_to_loss_limit(self):
        return self.next_step.price <= self.price

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
        if self.has_next_step():
            if self.is_sell:
                profit_or_loss = (self.next_step.source_currency_amount - self.source_currency_amount) * self.next_step.price
                profit_or_loss = profit_or_loss * self.next_step.price
            else:
                profit_or_loss = self.source_currency_amount * (self.next_step.price - self.price)
            currency = self.dest_currency_type
            return profit_or_loss, currency
        else:
            return 0, ''

    def get_total(self):
        return round(self.source_currency_amount * self.price, 2)

    def get_transferred_currency(self):
        if self.is_sell:
            return self.get_total(), self.dest_currency_type
        else:
            return self.source_currency_amount, self.source_currency_type

    def get_transfer_status(self):
        switcher = {
            'L': 'Waiting for permission',
            'TOS': 'Order was successful. Waiting to be done.',
            'TOU': 'Order was not successful.',
            'TOD': 'Done',
        }
        if self.needs_transfer():
            if self.status in switcher:
                return switcher[self.status]
            else:
                return 'Not started.'
        else:
            return 'Not needed'

    def update_status(self):
        pass

    def set_owner(self, owner):
        order = self
        while order is not None:
            order.owner = owner
            order.save()
            order = order.next_step

    def request_withdraw(self):
        account = self.get_account()
        currency = self.source_currency_type
        amount = self.source_currency_amount
        address = self.deposit_wallet_address
        return account.request_withdraw(currency, amount, address)
'''
needed fields for two step order:
owner, first_step_is_sell, price, account_type, second_step_account_type,
                            source_currency_type, dest_currency_type, source_currency_amount, profit_limit,
                            loss_limit, deposit_wallet_address

'''