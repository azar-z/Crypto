from django.test import TestCase

from trade.forms.order import OrderForm


def get_form_data(source_currency_type='BTC', is_sell='True', account_type='N',
                  source_currency_amount=1, price=40000, no_second_step='True',
                  second_step_account_type='W', max_price=41000, min_price=35000):
    return {
        'source_currency_type': source_currency_type,
        'is_sell': is_sell,
        'account_type': account_type,
        'source_currency_amount': source_currency_amount,
        'price': price,
        'no_second_step': no_second_step,
        'second_step_account_type': second_step_account_type,
        'max_price': max_price,
        'min_price': min_price
    }


class OrderFormTestCase(TestCase):
    def test_required_data_not_filled(self):
        form_data = {}
        form = OrderForm(data=form_data)
        self.assertTrue('This field is required.' in form.errors['source_currency_type'])
        self.assertTrue('This field is required.' in form.errors['is_sell'])
        self.assertTrue('This field is required.' in form.errors['account_type'])
        self.assertTrue('This field is required.' in form.errors['source_currency_amount'])
        self.assertTrue('This field is required.' in form.errors['price'])
        self.assertFalse('no_second_step' in form.errors)

    def test_zero_amount(self):
        form_data = get_form_data(source_currency_amount=0)
        form = OrderForm(data=form_data)
        self.assertTrue('Amount is too small' in form.errors['source_currency_amount'])

    def test_max_price_less_than_price(self):
        form_data = get_form_data(price=10, max_price=9)
        form = OrderForm(data=form_data)
        self.assertTrue('Maximum price should be greater than price' in form.errors['max_price'])

    def test_min_price_more_than_price(self):
        form_data = get_form_data(price=10, min_price=11)
        form = OrderForm(data=form_data)
        self.assertTrue('Minimum price should be less than price' in form.errors['min_price'])

    def test_successful_order_creation(self):
        form_data = get_form_data()
        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid())
