from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic

from user.models import Account


@method_decorator(login_required, name='dispatch')
class ComparePricesView(generic.TemplateView):
    template_name = 'user/trades/compare_prices.html'

    def get_context_data(self, **kwargs):
        context = super(ComparePricesView, self).get_context_data(**kwargs)
        additional_context = {
            'market_info': Account.get_market_info_of_all('IRR'),
        }
        context.update(additional_context)
        return context
