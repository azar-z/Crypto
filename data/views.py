from django.core.cache import cache
from django.shortcuts import render

from data.forms import PredictionForm


def bi_dashboard_view(request):
    cache_key = 'bi_dashboard_data'
    context = cache.get(cache_key)
    return render(request, 'data/bi_dashboard.html', context=context)


def get_name(request):
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            profit_percent = form.predict_profit_percent()
            return render(request, 'data/prediction.html', {'form': form, 'prediction': '%.2f' % profit_percent})
    else:
        form = PredictionForm()
    return render(request, 'data/prediction.html', {'form': form})
