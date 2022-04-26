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
    profit_limit = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True)
    loss_limit = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True)
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
            self.next_step.save()
        super(Order, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if self.has_next_step():
            self.next_step.delete(using, keep_parents)
        super(Order, self).delete(using, keep_parents)

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})

    def has_next_step(self):
        return self.next_step is not None

    def needs_transfer(self):
        return self.has_next_step() and self.account_type != self.next_step.account_type

    def get_account(self):
        return get_account_based_on_type(self.owner, self.account_type)

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

    def update_status_based_on_account_data(self):
        account = self.get_account()
        account_order_status = account.get_order_status(self.id_in_account)
        self.status = self.get_status_based_on_account_order_status(account_order_status)
        self.save()

    def check_limits(self, market_price):
        got_to_profit_limit = self._check_profit_limit(market_price)
        if not got_to_profit_limit:
            got_to_loss_limit = self._check_loss_limit(market_price)
            return got_to_loss_limit
        else:
            return got_to_profit_limit

    def _check_profit_limit(self, market_price):
        return self._check_limit(is_sell_condition=market_price <= self.profit_limit,
                                 limit_price=self.profit_limit)

    def _check_loss_limit(self, market_price):
        return self._check_limit(is_sell_condition=market_price >= self.loss_limit,
                                 limit_price=self.loss_limit)

    def _check_limit(self, is_sell_condition, limit_price):
        if self.has_next_step():
            got_to_limit = False
            if self.has_next_step():
                if self.is_sell:
                    if is_sell_condition:
                        self.next_step.price = limit_price
                        self.next_step.source_currency_amount = self.get_total() / limit_price
                        got_to_limit = True
                else:
                    if not is_sell_condition:
                        self.next_step.price = limit_price
                        self.next_step.source_currency_amount = self.source_currency_amount
                        got_to_limit = True
            if got_to_limit:
                self.status = 'L'
                self.save()
            return got_to_limit

    def got_to_profit_limit(self):
        return self.next_step.price == self.profit_limit

    def got_to_loss_limit(self):
        return self.next_step.price == self.loss_limit

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
                profit_or_loss = (
                                         self.next_step.source_currency_amount - self.source_currency_amount) * self.next_step.price
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

    def set_owner(self, owner):
        self.owner = owner
        self.save()
        if self.has_next_step():
            self.next_step.set_owner(owner)

    def request_withdraw(self):
        account = self.get_account()
        currency = self.source_currency_type
        amount = self.source_currency_amount
        address = self.deposit_wallet_address
        return account.request_withdraw(currency, amount, address)

    def get_profit_percent(self):
        if self.profit_limit > self.price:
            lower_price = self.price
            higher_price = self.profit_limit
        else:
            lower_price = self.profit_limit
            higher_price = self.price
        return round((higher_price - lower_price) / lower_price * 100, 2)

    def get_form_initials(self):
        return {
            'source_currency_type': self.source_currency_type,
            'is_sell': self.is_sell,
            'account_type': self.account_type,
            'price': round(float(self.price), 2),
            'no_second_step': False,
            'profit_limit': round(float(self.profit_limit), 2),
            'second_step_account_type': self.next_step.account_type,
        }

    @staticmethod
    def save_golden_trades():
        golden_trades = Order.objects.filter(owner=None, previous_step=None)
        for golden_trade in golden_trades:
            golden_trade.delete()
        market_info_of_all_currencies = Account.get_market_info_of_all()
        for market_info in market_info_of_all_currencies:
            Order._save_golden_trades_of_currency(market_info['currency'], market_info['info'])

    @staticmethod
    def _save_golden_trades_of_currency(currency, market_info):
        for sub1 in Account.__subclasses__():
            for sub2 in Account.__subclasses__():
                if sub2 is not sub1:
                    sub1_lowest_price = market_info[sub1.__name__.lower()]['bestBuy']
                    sub2_highest_price = market_info[sub2.__name__.lower()]['bestSell']
                    Order._save_trade_if_golden(first_account=sub1.get_type(), second_account=sub2.get_type(),
                                                first_lowest_price=sub1_lowest_price,
                                                second_highest_price=sub2_highest_price, source=currency)

    @staticmethod
    def _save_trade_if_golden(first_account, second_account, first_lowest_price, second_highest_price,
                              source, dest='USDT'):
        if first_lowest_price < second_highest_price:
            if second_highest_price / first_lowest_price - 1 > 0.002:
                Order._create_golden_trade(source, dest, first_account, second_account, second_highest_price, False,
                                           first_lowest_price)
                Order._create_golden_trade(source, dest, second_account, first_account, first_lowest_price, True,
                                           second_highest_price)

    @staticmethod
    def _create_golden_trade(source, dest, first_account, second_account, profit_limit, is_sell, first_price):
        second_step = Order.objects.create(account_type=second_account, is_sell=not is_sell,
                                           source_currency_type=source, dest_currency_type=dest)
        second_step.save()
        first_step = Order.objects.create(next_step=second_step, source_currency_type=source, dest_currency_type=dest,
                                          account_type=first_account,
                                          profit_limit=profit_limit, is_sell=is_sell, price=first_price)
        first_step.save()

    @staticmethod
    def update_status():
        try:
            Order.update_os_to_od()
            Order.update_od_to_l_to_next_step_os()
            Order.update_tos_to_td_to_next_step_os()
        except NoAuthenticationInformation:
            pass

    @staticmethod
    def update_os_to_od():
        orders = Order.objects.filter(status='OS').exclude(owner=None)
        for order in orders:
            order.update_status_based_on_account_data()

    @staticmethod
    def update_od_to_l_to_next_step_os():
        orders = Order.objects.filter(status='OD').exclude(owner=None)
        for order in orders:
            if order.has_next_step():
                account = order.next_step.get_account()
                market_price = account.get_average_market_price()
                got_to_limit = order.check_limits(market_price)
                if got_to_limit and not order.needs_transfer():
                    order.next_step.order_transaction()

    @staticmethod
    def update_tos_to_td_to_next_step_os():
        orders = Order.objects.filter(status='TOS').exclude(owner=None)
        for order in orders:
            if order.has_next_step():
                transfer_done = order.next_step.check_for_enough_balance()
                if transfer_done:
                    order.status = 'TD'
                    order.save()
                    order.next_step.order_transaction()

    @staticmethod
    def get_status_based_on_account_order_status(account_order_status):
        if account_order_status == AccountOrderStatus.DONE:
            status = 'OD'
        elif account_order_status == AccountOrderStatus.CANCELLED:
            status = 'OU'
        else:
            status = 'OS'
        return status


'''
needed fields for two step order:
owner, first_step_is_sell, price, account_type, second_step_account_type,
                            source_currency_type, dest_currency_type, source_currency_amount, profit_limit,
                            loss_limit, deposit_wallet_address

'''
