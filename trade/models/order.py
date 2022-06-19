from django.db import models
from django.urls import reverse
from django.utils import timezone

from trade.utils import SOURCE_CURRENCIES, DEST_CURRENCIES, AccountOrderStatus
from user.errors import NoAuthenticationInformation
from user.logics.accounts import get_account_based_on_type
from user.models import BaseModel, User
from user.models.account import ACCOUNT_TYPE_CHOICES, Account

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

GOLDEN_TRADE_PROFIT_LIMIT_PERCENT = 2


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
    max_price = models.DecimalField(verbose_name='Maximum Price  (USDT)', max_digits=20, decimal_places=2, default=0, blank=True)
    min_price = models.DecimalField(verbose_name='Minimum Price  (USDT)', max_digits=20, decimal_places=2, default=0, blank=True)
    deposit_wallet_address = models.CharField(max_length=200, null=True, default=None, blank=True)
    withdraw_id = models.CharField(max_length=200, null=True, default=None, blank=True)
    transfer_fee = models.DecimalField(max_digits=15, decimal_places=5, default=0.0)
    next_step = models.OneToOneField('self', null=True, blank=True, on_delete=models.SET_NULL, default=None,
                                     related_name='previous_step')

    class Meta:
        ordering = ('-updated',)

    def __str__(self):
        if self.owner is not None:
            return 'order' + '_' + str(self.id) + '_' + self.owner.username
        else:
            return 'golden_trade_' + str(self.id)

    def save(self, *args, **kwargs):
        if self.has_next_step():
            if self.owner != self.next_step.owner:
                self.next_step.owner = self.owner
            self.next_step.save()
        super(Order, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if self.has_next_step():
            self.next_step.delete(using, keep_parents)
        super(Order, self).delete(using, keep_parents)

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})

    def get_date(self):
        return self.time.date()

    def has_next_step(self):
        return self.next_step is not None

    def needs_transfer(self):
        return self.has_next_step() and self.account_type != self.next_step.account_type

    def get_account(self):
        return get_account_based_on_type(self.owner, self.account_type)

    def get_profit_limit(self):
        profit_limit = self.min_price if self.is_sell else self.max_price
        return profit_limit

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

    def update_transaction_status(self):
        account = self.get_account()
        account_order_status = account.get_order_status(self.id_in_account)
        self.status = self.get_status_based_on_account_order_status(account_order_status)
        self.save()

    def _check_limits(self, market_price):
        if not self.has_next_step():
            return False
        got_to_max_price = market_price >= self.max_price
        got_to_min_price = market_price <= self.min_price
        got_to_limit = got_to_max_price or got_to_min_price
        if got_to_limit:
            if got_to_min_price:
                price = self.min_price
            elif got_to_max_price:
                price = self.max_price
            self.do_got_to_limit_actions(price)
        return got_to_limit

    def do_got_to_limit_actions(self, price):
        if self.has_next_step():
            if self.is_sell:
                self.next_step.price = price
                self.next_step.source_currency_amount = self.get_total() / price
            else:
                self.next_step.price = price
                self.next_step.source_currency_amount = self.source_currency_amount
            self.status = 'L'
            self.save()

    def got_to_max_price(self):
        return self.next_step.price == self.max_price

    def got_to_min_price(self):
        return self.next_step.price == self.min_price

    def check_for_enough_balance(self):
        account = self.get_account()
        spent_currency = self.get_spent_currency()
        spent_currency_amount = spent_currency[0]
        spent_currency_type = spent_currency[1]
        spent_currency_balance = account.get_balance(spent_currency_type)
        if spent_currency_balance >= spent_currency_amount:
            return True
        return False

    def get_profit_or_loss(self):
        if self.has_next_step():
            if self.is_sell:
                profit_or_loss = (self.next_step.source_currency_amount - self.source_currency_amount) * self.next_step.price
            else:
                profit_or_loss = self.source_currency_amount * (self.next_step.price - self.price)
            currency = self.dest_currency_type
            return profit_or_loss, currency
        else:
            return 0, ''

    def get_total(self):
        return round(self.source_currency_amount * self.price, 2)

    def get_gained_currency(self):
        if self.is_sell:
            return self.get_total(), self.dest_currency_type
        else:
            return self.source_currency_amount, self.source_currency_type

    def get_spent_currency(self):
        if not self.is_sell:
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

    def request_withdraw(self):
        account = self.get_account()
        currency = self.get_gained_currency()
        currency_amount = currency[0]
        currency_type = currency[1]
        address = self.deposit_wallet_address
        return account.request_withdraw(currency_type, currency_amount, address)

    def get_profit_percent_for_golden_trade(self):
        profit_limit = self.get_profit_limit()
        if profit_limit > self.price:
            lower_price = self.price
            higher_price = profit_limit
        else:
            lower_price = profit_limit
            higher_price = self.price
        return round((higher_price / lower_price) * 100 - 100, 2)

    def get_form_initials(self):
        return {
            'source_currency_type': self.source_currency_type,
            'source_currency_amount': round(float(self.source_currency_amount), 5),
            'is_sell': self.is_sell,
            'account_type': self.account_type,
            'price': round(float(self.price), 2),
            'no_second_step': False,
            'max_price': round(float(self.max_price), 2),
            'min_price': round(float(self.min_price), 2),
            'second_step_account_type': self.next_step.account_type,
        }

    def update_status(self):
        if self.status == 'OS':
            self.update_transaction_status()
        if self.has_next_step():
            if self.status == 'OD':
                self.check_limits()
            if not self.needs_transfer():
                if self.status == 'L':
                    self.next_step.order_transaction()
            else:
                if self.status == 'TOS':
                    self.update_transfer_status()
                if self.status == 'TD':
                    self.next_step.order_transaction()

    def check_limits(self):
        if self.has_next_step():
            account = self.next_step.get_account()
            market_price = account.get_average_market_price(self.source_currency_type, self.dest_currency_type)
            got_to_limit = self._check_limits(market_price)
            return got_to_limit

    def update_transfer_status(self):
        transfer_done = self.next_step.check_for_enough_balance()
        if transfer_done:
            self.status = 'TD'
            self.save()

    def is_golden(self):
        return self.get_profit_percent_for_golden_trade() > GOLDEN_TRADE_PROFIT_LIMIT_PERCENT

    @staticmethod
    def save_golden_trades():
        golden_trades = Order.objects.filter(owner=None, previous_step=None)
        for golden_trade in golden_trades:
            golden_trade.delete()
        market_info_of_all_currencies = Account.get_market_info_of_all()
        for market_info in market_info_of_all_currencies:
            Order.save_golden_trades_of_currency(market_info['currency'], market_info['info'])

    @staticmethod
    def save_golden_trades_of_currency(currency, market_info):
        for sub1 in Account.__subclasses__():
            for sub2 in Account.__subclasses__():
                if sub2 is not sub1:
                    sub1_lowest_price = market_info[sub1.__name__.lower()]['bestBuy']
                    sub2_highest_price = market_info[sub2.__name__.lower()]['bestSell']
                    Order.save_trades_if_golden(first_account=sub1.get_type(), second_account=sub2.get_type(),
                                                first_lowest_price=sub1_lowest_price,
                                                second_highest_price=sub2_highest_price,
                                                source=currency, dest='USDT')

    @staticmethod
    def save_trades_if_golden(first_account, second_account, first_lowest_price, second_highest_price,
                              source, dest):
        if first_lowest_price < second_highest_price:
            order = Order.create_trade(source, dest, first_account, second_account, second_highest_price, False,
                                       first_lowest_price)
            if order.is_golden():
                order.save()
            order = Order.create_trade(source, dest, second_account, first_account, first_lowest_price, True,
                                       second_highest_price)
            if order.is_golden():
                order.save()

    @staticmethod
    def create_trade(source, dest, first_account, second_account, profit_limit, is_sell, first_price):
        second_step = Order(account_type=second_account, is_sell=not is_sell,
                            source_currency_type=source, dest_currency_type=dest, price=profit_limit)
        min_price = max_price = profit_limit
        if is_sell:
            max_price = first_price * 2
        else:
            min_price = first_price / 2
        first_step = Order(next_step=second_step, source_currency_type=source, dest_currency_type=dest,
                           account_type=first_account,
                           min_price=min_price, max_price=max_price, is_sell=is_sell, price=first_price)
        return first_step

    @staticmethod
    def update_status_of_all_orders():
        orders = Order.objects.exclude(owner=None)
        for order in orders:
            try:
                order.update_status()
            except NoAuthenticationInformation:
                pass

    @staticmethod
    def get_status_based_on_account_order_status(account_order_status):
        if account_order_status == AccountOrderStatus.DONE:
            status = 'OD'
        elif account_order_status == AccountOrderStatus.CANCELLED:
            status = 'OU'
        else:
            status = 'OS'
        return status
