import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import generic

from trade.forms.order import OrderForm
from trade.models import Order
from user.errors import NoAuthenticationInformation
from user.models import Account


@method_decorator(login_required, name='dispatch')
class NewTradeView(generic.CreateView):
    model = Order
    template_name = 'trade/new_trade.html'
    form_class = OrderForm

    def form_valid(self, form):
        response = super(NewTradeView, self).form_valid(form)
        order = self.object
        order.owner = self.request.user
        order.save()
        try:
            order.order_transaction()
        except NoAuthenticationInformation:
            messages.error(self.request, 'We need valid authentication information for ordering a transaction')
            return redirect('accounts', account_type=order.account_type)
        return response

    def get_initial(self):
        initial = super().get_initial()
        if 'initial' in self.request.GET:
            data = self.request.GET['initial']
            data = json.loads(data)
            initial.update(data)
        elif 'account_type' in self.request.GET:
            initial['account_type'] = self.request.GET['account_type']
            initial['second_step_account_type'] = self.request.GET['account_type']
            initial['price'] = self.request.GET['price']
            initial['source_currency_type'] = self.request.GET['source_currency_type']
        return initial


def get_orderbook_and_trades_view(request):
    source_currency = request.GET.get('source_currency_type', None)
    dest_currency = 'USDT'
    if source_currency is not None and dest_currency is not None and source_currency != '' and dest_currency != '':
        context = {
            'is_valid': True,
            'orderbook_bids': Account.get_orderbook_of_all(source_currency, dest_currency, True),
            'orderbook_asks': Account.get_orderbook_of_all(source_currency, dest_currency, False),
            'trades_sell': Account.get_trades_of_all(source_currency, dest_currency, True),
            'trades_buy': Account.get_trades_of_all(source_currency, dest_currency, False),
        }
    else:
        context = {
            'is_valid': False,
        }
    return render(request, 'trade/orderbook_and_trades.html', context=context)
