from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from data.forms import PredictionForm


@login_required
@user_passes_test(lambda u: u.is_superuser)
def bi_dashboard_view(request):
    cache_key = 'bi_dashboard_data'
    context = cache.get(cache_key)
    return render(request, 'data/bi_dashboard.html', context=context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def predict_user_profit(request):
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            profit_percent = form.predict_profit_percent()
            return render(request, 'data/user_profit_prediction.html', {'form': form, 'prediction': '%.2f' % profit_percent})
    else:
        form = PredictionForm()
    return render(request, 'data/user_profit_prediction.html', {'form': form})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class PredictBTCPrice(TemplateView):
    template_name = 'data/btc_price_prediction.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cache_key = 'BTC_price_prediction'
        BTC_price_prediction = cache.get(cache_key)
        context['BTC_price_prediction'] = BTC_price_prediction
        return context

