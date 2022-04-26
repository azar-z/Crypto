import environ
from django.test import TestCase

from trade.fake_data_utils import create_one_step_order, create_two_step_order
from trade.models import Order
from user.errors import NoAuthenticationInformation
from user.fake_data_utils import create_fake_user

env = environ.Env()
environ.Env.read_env()
NOBITEX_TOKEN = env('NOBITEX_TOKEN')
NOBITEX_DONE_ORDER_ID = env('NOBITEX_DONE_ORDER_ID')


class OrderModelTestCase(TestCase):
    def create_user(self):
        return create_fake_user()

    def create_order(self, owner=None, is_two_step=False):
        if is_two_step:
            order = create_two_step_order(owner)
        else:
            order = create_one_step_order(owner)
        return order

    def make_order_impossible(self, order):
        order.source_currency_type = 'BTC'
        order.amount = '1'
        order.save()

    def make_user_authenticated(self, user, account_type='N'):
        if account_type == 'N':
            user.nobitex_account.token = NOBITEX_TOKEN
            user.nobitex_account.save()

    def make_order_authenticated(self, order, account_type='N'):
        order.account_type = account_type
        order.save()
        self.make_user_authenticated(order.owner, account_type)

    def set_limits_for_two_step_order(self, order, is_sell, price=187.99,
                                      lower_price=98.00,
                                      higher_price=243.77):
        order.status = 'OD'
        order.is_sell = is_sell
        order.price = price
        order.next_step.is_sell = not is_sell
        if order.is_sell:
            order.loss_limit = higher_price
            order.profit_limit = lower_price
        else:
            order.loss_limit = lower_price
            order.profit_limit = higher_price
        order.save()

    def create_n_step_order(self, n, owner=None):
        first_order = self.create_order(owner)
        order = first_order
        for _ in range(n - 1):
            order.next_step = self.create_order(owner)
            order.save()
            order = order.next_step
        return first_order

    def setUp(self):
        self.user = create_fake_user()
        self.one_step_order = self.create_order(self.user)
        self.two_step_order = self.create_order(self.user, is_two_step=True)

    def test_delete_one_step_order(self):
        self.one_step_order.delete()
        self.assertEqual(Order.objects.filter(id=self.one_step_order.id).count(), 0)

    def test_delete_two_step_order(self):
        self.two_step_order.delete()
        self.assertEqual(Order.objects.filter(id=self.two_step_order.id).count(), 0)
        self.assertEqual(Order.objects.filter(id=self.two_step_order.next_step.id).count(), 0)

    def test_delete_ten_step_order(self):
        n_step_order = self.create_n_step_order(10)
        order_count_before_deletion = Order.objects.count()
        n_step_order.delete()
        order_count_after_deletion = Order.objects.count()
        self.assertEqual(order_count_before_deletion, order_count_after_deletion + 10)

    def test_get_absolute_url(self):
        order = self.one_step_order
        url = order.get_absolute_url()
        self.assertEqual(url, '/trade/orders/%d/' % order.id)

    def test_has_next_step(self):
        self.assertFalse(self.one_step_order.has_next_step())
        self.assertTrue(self.two_step_order.has_next_step())

    def test_needs_transfer_one_step_order(self):
        self.assertFalse(self.one_step_order.needs_transfer())

    def test_needs_transfer_two_step_no_transfer_order(self):
        two_step_order = self.two_step_order
        two_step_order.account_type = 'N'
        two_step_order.next_step.account_type = 'N'
        two_step_order.save()
        self.assertFalse(two_step_order.needs_transfer())

    def test_needs_transfer_two_step_with_transfer_order(self):
        two_step_order = self.two_step_order
        two_step_order.account_type = 'N'
        two_step_order.next_step.account_type = 'W'
        two_step_order.save()
        self.assertTrue(two_step_order.needs_transfer())

    def test_get_account(self):
        order = self.one_step_order
        order.account_type = 'N'
        order.save()
        self.assertEqual(order.get_account(), order.owner.nobitex_account)
        order.account_type = 'W'
        order.save()
        self.assertEqual(order.get_account(), order.owner.wallex_account)
        order.account_type = 'E'
        order.save()
        self.assertEqual(order.get_account(), order.owner.exir_account)

    def test_order_transaction_no_authentication_info(self):
        order = self.one_step_order
        self.assertRaises(NoAuthenticationInformation, order.order_transaction)

    def test_order_transaction_not_possible_order(self):
        order = self.one_step_order
        order.status = 'NO'
        order.save()
        self.make_order_authenticated(order)
        self.make_order_impossible(order)
        try:
            order.order_transaction()
        except NoAuthenticationInformation:
            self.fail("NoAuthenticationInformation")
        self.assertEqual(order.status, 'OU')

    def test_update_status_based_on_account_data_done_order(self):
        order = self.one_step_order
        order.status = 'OS'
        order.id_in_account = NOBITEX_DONE_ORDER_ID
        order.save()
        self.make_order_authenticated(order)
        try:
            order.update_status_based_on_account_data()
        except NoAuthenticationInformation:
            self.fail("NoAuthenticationInformation")
        self.assertEqual(order.status, 'OD')

    def test_update_status_based_on_account_data_wrong_id(self):
        order = self.one_step_order
        order.status = 'OS'
        order.id_in_account = 0
        order.save()
        self.make_order_authenticated(order)
        try:
            order.update_status_based_on_account_data()
        except NoAuthenticationInformation:
            self.fail("NoAuthenticationInformation")
        self.assertEqual(order.status, 'OU')

    def test_check_limits_no_next_step(self):
        one_step_order = self.one_step_order
        one_step_order.status = 'OD'
        result = one_step_order.check_limits(1000)
        self.assertFalse(result)
        self.assertEqual(one_step_order.status, 'OD')

    def test_check_limits_sell_not_got_to_limit(self):
        two_step_order = self.two_step_order
        self.set_limits_for_two_step_order(two_step_order, is_sell=True)
        market_price = (two_step_order.profit_limit + two_step_order.loss_limit) / 2
        two_step_order.check_limits(market_price)
        self.assertNotEqual(two_step_order.status, 'L')
        self.assertEqual(two_step_order.status, 'OD')

    def test_check_limits_sell_got_to_profit_limit(self):
        two_step_order = self.two_step_order
        self.set_limits_for_two_step_order(two_step_order, is_sell=True)
        market_price = two_step_order.profit_limit / 2
        two_step_order.check_limits(market_price)
        self.assertEqual(two_step_order.status, 'L')
        self.assertEqual(two_step_order.profit_limit, two_step_order.next_step.price)

    def test_check_limits_sell_got_to_loss_profit_limit(self):
        two_step_order = self.two_step_order
        self.set_limits_for_two_step_order(two_step_order, is_sell=True)
        market_price = two_step_order.loss_limit * 2
        two_step_order.check_limits(market_price)
        self.assertEqual(two_step_order.status, 'L')
        self.assertEqual(two_step_order.loss_limit, two_step_order.next_step.price)

    def test_check_limits_buy_not_got_to_limit(self):
        two_step_order = self.two_step_order
        self.set_limits_for_two_step_order(two_step_order, is_sell=False)
        market_price = (two_step_order.profit_limit + two_step_order.loss_limit) / 2
        two_step_order.check_limits(market_price)
        self.assertNotEqual(two_step_order.status, 'L')
        self.assertEqual(two_step_order.status, 'OD')

    def test_check_limits_buy_got_to_profit_limit(self):
        two_step_order = self.two_step_order
        self.set_limits_for_two_step_order(two_step_order, is_sell=False)
        market_price = two_step_order.profit_limit * 2
        two_step_order.check_limits(market_price)
        self.assertEqual(two_step_order.status, 'L')
        self.assertEqual(two_step_order.profit_limit, two_step_order.next_step.price)

    def test_check_limits_buy_got_to_loss_profit_limit(self):
        two_step_order = self.two_step_order
        self.set_limits_for_two_step_order(two_step_order, is_sell=False)
        market_price = two_step_order.loss_limit / 2
        two_step_order.check_limits(market_price)
        self.assertEqual(two_step_order.status, 'L')
        self.assertEqual(two_step_order.loss_limit, two_step_order.next_step.price)


'''
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
                got_to_limit = order.check_for_profit_or_loss_limits()
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
# TODO: test_order_transaction_successful
