from django.test import TestCase

from trade.models import Order
from trade.models.order import GOLDEN_TRADE_PROFIT_LIMIT_PERCENT
from trade.tests.utils import *
from user.errors import NoAuthenticationInformation


class OrderModelTestCase(TestCase):

    def setUp(self):
        self.user = create_user()
        self.one_step_order = create_order(self.user)
        self.two_step_order = create_order(self.user, is_two_step=True)

    def test_save_owner_change_ten_step_order(self):
        old_owner = create_user()
        order = create_n_step_order(10, old_owner)
        new_owner = create_user()
        self.assertEqual(new_owner.orders.count(), 0)
        self.assertEqual(old_owner.orders.count(), 10)
        order.owner = new_owner
        order.save()
        self.assertEqual(new_owner.orders.count(), 10)
        self.assertEqual(old_owner.orders.count(), 0)

    def test_delete_one_step_order(self):
        self.one_step_order.delete()
        self.assertEqual(Order.objects.filter(id=self.one_step_order.id).count(), 0)

    def test_delete_two_step_order(self):
        self.two_step_order.delete()
        self.assertEqual(Order.objects.filter(id=self.two_step_order.id).count(), 0)
        self.assertEqual(Order.objects.filter(id=self.two_step_order.next_step.id).count(), 0)

    def test_delete_ten_step_order(self):
        n_step_order = create_n_step_order(10)
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
        make_order_authenticated(order)
        make_order_impossible(order)
        try:
            order.order_transaction()
        except NoAuthenticationInformation:
            self.fail("NoAuthenticationInformation")
        self.assertEqual(order.status, 'OU')

    def test_update_transaction_status_done_order(self):
        order = self.one_step_order
        order.status = 'OS'
        order.id_in_account = NOBITEX_DONE_ORDER_ID
        order.save()
        make_order_authenticated(order)
        try:
            order.update_transaction_status()
        except NoAuthenticationInformation:
            self.fail("NoAuthenticationInformation")
        self.assertEqual(order.status, 'OD')

    def test_update_transaction_status_wrong_id(self):
        order = self.one_step_order
        order.status = 'OS'
        order.id_in_account = 0
        order.save()
        make_order_authenticated(order)
        try:
            order.update_transaction_status()
        except NoAuthenticationInformation:
            self.fail("NoAuthenticationInformation")
        self.assertEqual(order.status, 'OU')

    def test_check_limits_no_next_step(self):
        one_step_order = self.one_step_order
        one_step_order.status = 'OD'
        result = one_step_order._check_limits(1000)
        self.assertFalse(result)
        self.assertEqual(one_step_order.status, 'OD')

    def test_check_limits_not_got_to_limit(self):
        two_step_order = self.two_step_order
        set_limits_for_two_step_order(two_step_order, is_sell=True)
        market_price = (two_step_order.max_price + two_step_order.min_price) / 2
        two_step_order._check_limits(market_price)
        self.assertNotEqual(two_step_order.status, 'L')
        self.assertEqual(two_step_order.status, 'OD')

    def test_check_limits_got_to_max_price(self):
        two_step_order = self.two_step_order
        set_limits_for_two_step_order(two_step_order, is_sell=True)
        market_price = two_step_order.max_price * 2
        two_step_order._check_limits(market_price)
        self.assertEqual(two_step_order.status, 'L')
        self.assertEqual(two_step_order.max_price, two_step_order.next_step.price)

    def test_check_limits_got_to_min_price(self):
        two_step_order = self.two_step_order
        set_limits_for_two_step_order(two_step_order, is_sell=True)
        market_price = two_step_order.min_price / 2
        two_step_order._check_limits(market_price)
        self.assertEqual(two_step_order.status, 'L')
        self.assertEqual(two_step_order.min_price, two_step_order.next_step.price)

    def test_get_total(self):
        order = self.one_step_order
        order.price = 100
        order.source_currency_amount = 10
        order.save()
        self.assertEqual(order.get_total(), 1000)

    def test_get_gained_currency_sell(self):
        order = self.one_step_order
        order.is_sell = True
        order.save()
        gained_currency = order.get_gained_currency()
        gained_currency_amount = gained_currency[0]
        gained_currency_type = gained_currency[1]
        self.assertEqual(order.dest_currency_type, gained_currency_type)
        self.assertEqual(order.get_total(), gained_currency_amount)

    def test_get_gained_currency_buy(self):
        order = self.one_step_order
        order.is_sell = False
        order.save()
        gained_currency = order.get_gained_currency()
        gained_currency_amount = gained_currency[0]
        gained_currency_type = gained_currency[1]
        self.assertEqual(order.source_currency_type, gained_currency_type)
        self.assertEqual(order.source_currency_amount, gained_currency_amount)

    def test_get_spent_currency_buy(self):
        order = self.one_step_order
        order.is_sell = False
        order.save()
        gained_currency = order.get_spent_currency()
        gained_currency_amount = gained_currency[0]
        gained_currency_type = gained_currency[1]
        self.assertEqual(order.dest_currency_type, gained_currency_type)
        self.assertEqual(order.get_total(), gained_currency_amount)

    def test_get_spent_currency_sell(self):
        order = self.one_step_order
        order.is_sell = True
        order.save()
        gained_currency = order.get_spent_currency()
        gained_currency_amount = gained_currency[0]
        gained_currency_type = gained_currency[1]
        self.assertEqual(order.source_currency_type, gained_currency_type)
        self.assertEqual(order.source_currency_amount, gained_currency_amount)

    def test_get_profit_percent_for_golden_trade_sell(self):
        two_step_order = self.two_step_order
        set_limits_for_two_step_order(two_step_order, True)
        price = two_step_order.price
        profit_limit = two_step_order.get_profit_limit()
        self.assertEqual(two_step_order.get_profit_percent_for_golden_trade(), round(price / profit_limit * 100 - 100, 2))

    def test_get_profit_percent_for_golden_trade_buy(self):
        two_step_order = self.two_step_order
        set_limits_for_two_step_order(two_step_order, False)
        price = two_step_order.price
        profit_limit = two_step_order.get_profit_limit()
        self.assertEqual(two_step_order.get_profit_percent_for_golden_trade(), round(profit_limit / price * 100 - 100, 2))

    def test_save_trades_if_golden_not_golden_low_percent(self):
        Order.objects.all().delete()
        price = 200
        higher_price = (GOLDEN_TRADE_PROFIT_LIMIT_PERCENT / 2 + 100) / 100 * price
        Order.save_trades_if_golden('N', 'W', price, higher_price, 'BTC', 'USDT')
        self.assertEqual(Order.objects.filter(owner=None).count(), 0)

    def test_save_trades_if_golden_not_golden_negative_percent(self):
        Order.objects.all().delete()
        price = 200
        higher_price = 400
        Order.save_trades_if_golden('N', 'W', higher_price, price, 'BTC', 'USDT')
        self.assertEqual(Order.objects.filter(owner=None).count(), 0)

    def test_save_trades_if_golden_successful(self):
        Order.objects.all().delete()
        price = 200
        higher_price = (GOLDEN_TRADE_PROFIT_LIMIT_PERCENT * 2 + 100) / 100 * price
        Order.save_trades_if_golden('N', 'W', price, higher_price, 'BTC', 'USDT')
        self.assertEqual(Order.objects.filter(owner=None, previous_step=None).count(), 2)
        self.assertEqual(Order.objects.filter(source_currency_type='BTC', dest_currency_type='USDT', account_type='N',
                                              next_step__account_type='W', is_sell=False).count(), 1)
        self.assertEqual(Order.objects.filter(source_currency_type='BTC', dest_currency_type='USDT', account_type='W',
                                              next_step__account_type='N', is_sell=True).count(), 1)

    def test_get_profit_or_loss_sell_profit(self):
        two_step_order = self.two_step_order
        two_step_order.is_sell = True
        two_step_order.price = 100
        two_step_order.source_currency_amount = 1
        two_step_order.next_step.price = 50
        two_step_order.next_step.source_currency_amount = 2
        two_step_order.save()
        self.assertEqual(two_step_order.get_profit_or_loss()[0], 50)

    def test_get_profit_or_loss_sell_loss(self):
        two_step_order = self.two_step_order
        two_step_order.is_sell = True
        two_step_order.price = 100
        two_step_order.source_currency_amount = 2
        two_step_order.next_step.price = 200
        two_step_order.next_step.source_currency_amount = 1
        two_step_order.save()
        self.assertEqual(two_step_order.get_profit_or_loss()[0], -200)

    def test_get_profit_or_loss_buy_profit(self):
        two_step_order = self.two_step_order
        two_step_order.is_sell = False
        two_step_order.price = 100
        two_step_order.source_currency_amount = 2
        two_step_order.next_step.price = 300
        two_step_order.next_step.source_currency_amount = 2
        two_step_order.save()
        self.assertEqual(two_step_order.get_profit_or_loss()[0], 400)

    def test_get_profit_or_loss_buy_loss(self):
        two_step_order = self.two_step_order
        two_step_order.is_sell = False
        two_step_order.price = 100
        two_step_order.source_currency_amount = 2
        two_step_order.next_step.price = 30
        two_step_order.next_step.source_currency_amount = 2
        two_step_order.save()
        self.assertEqual(two_step_order.get_profit_or_loss()[0], -140)
