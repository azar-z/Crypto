from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic

from trade.models import Order
from user.models import Account


@method_decorator(login_required, name='dispatch')
class NewTradeView(generic.CreateView):
    model = Order
    template_name = 'user/trades/new_trade.html'
    fields = ['first_step_account_type', 'source_currency_type', 'dest_currency_type',
              'source_currency_amount', 'price', 'is_sell', 'second_step_account_type', 'profit_limit', 'loss_limit']

    def get_context_data(self, **kwargs):
        context = super(NewTradeView, self).get_context_data(**kwargs)
        additional_context = {
            'orderbook_bids': Account.get_orderbook_of_all('BTC', 'IRR', True),
            'orderbook_asks': Account.get_orderbook_of_all('BTC', 'IRR', False),
            'trades_sell': Account.get_trades_of_all('BTC', 'IRR', True),
            'trades_buy': Account.get_trades_of_all('BTC', 'IRR', False),
        }
        context.update(additional_context)
        return context
