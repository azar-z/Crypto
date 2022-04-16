from django.views import generic

from user.models import Account


class ComparePricesView(generic.TemplateView):
    template_name = 'trade/compare_prices.html'

    def get_context_data(self, **kwargs):
        context = super(ComparePricesView, self).get_context_data(**kwargs)
        additional_context = {
            'market_info': Account.get_market_info_of_all('IRR'),
        }
        context.update(additional_context)
        return context
