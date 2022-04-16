import django_filters
from bootstrap_datepicker_plus.widgets import DateTimePickerInput

from trade.models import Order


class OrderListFilterSet(django_filters.FilterSet):
    first_step_time = django_filters.DateTimeFilter(label='From', widget=DateTimePickerInput(), lookup_expr='gt')
    second_step_time = django_filters.DateTimeFilter(label='Till', widget=DateTimePickerInput(), lookup_expr='lt')

    class Meta:
        model = Order
        fields = ['first_step_time', 'second_step_time']
