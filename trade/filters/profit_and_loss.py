import django_filters
from bootstrap_datepicker_plus.widgets import DateTimePickerInput

from trade.models import Order


class ProfitAndLossFilterSet(django_filters.FilterSet):
    time = django_filters.DateTimeFilter(label='From', widget=DateTimePickerInput(), lookup_expr='gt')
    next_step__time = django_filters.DateTimeFilter(label='Till', widget=DateTimePickerInput(), lookup_expr='lt')

    class Meta:
        model = Order
        fields = ['time', 'next_step__time', 'source_currency_type']
