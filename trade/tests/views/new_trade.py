from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from django.test.client import RequestFactory

from trade.forms.order import OrderForm
from trade.models import Order
from trade.tests.utils import create_user, create_order, make_user_authenticated_in_account
from trade.views import NewTradeView


class NewTradeViewTestCase(TestCase):

    def setUp(self):
        self.user = create_user()
        self.factory = RequestFactory()

    def get_request(self):
        request = self.factory.post(reverse('new_trade'), data={})
        request.user = self.user
        request._messages = messages.storage.default_storage(request)
        return request

    def get_view(self):
        request = self.get_request()
        view = NewTradeView(request=request)
        return view

    def get_valid_form(self, account_type='N'):
        order = create_order(None, True)
        order.account_type = account_type
        order.save()
        initials = order.get_form_initials()
        form = OrderForm(initials)
        return form

    def login_user(self):
        self.client.force_login(self.user)

    def test_login_required(self):
        data = {
        }
        response = self.client.post(reverse('new_trade'), data=data, follow=True)
        self.assertRedirects(response, reverse('login') + '?next=%2Ftrade%2Fnew%2F')

    def test_logged_in_user(self):
        self.login_user()
        data = {
        }
        response = self.client.post(reverse('new_trade'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_form_appears(self):
        self.login_user()
        response = self.client.get(reverse('new_trade'))
        self.assertContains(response, 'Order a new trade', html=True)
        self.assertContains(response, 'Maximum Price', html=True)
        self.assertContains(response, 'Minimum Price', html=True)

    def test_form_valid_no_authentication_data(self):
        self.login_user()
        form = self.get_valid_form()
        view = self.get_view()
        response = view.form_valid(form)
        response.client = self.client
        self.assertRedirects(response, reverse('accounts', kwargs={'account_type': 'N'}))

    def test_form_valid_set_owner(self):
        self.login_user()
        make_user_authenticated_in_account(self.user)
        form = self.get_valid_form()
        view = self.get_view()
        self.assertEqual(Order.objects.filter(owner=self.user).count(), 0)
        view.form_valid(form)
        self.assertNotEqual(Order.objects.filter(owner=self.user).count(), 0)

