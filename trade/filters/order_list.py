import django_filters
from bootstrap_datepicker_plus.widgets import DateTimePickerInput

from trade.models import Order


class OrderListFilterSet(django_filters.FilterSet):
    time = django_filters.DateTimeFilter(label='From', widget=DateTimePickerInput(), lookup_expr='gt')
    time_lt = django_filters.DateTimeFilter(field_name='time', label='Till', widget=DateTimePickerInput(), lookup_expr='lt')

    def __init__(self, *args, **kwargs):
        super(OrderListFilterSet, self).__init__(*args, **kwargs)
        self.filters['account_type'].label = "First Action In:"
        self.filters['next_step__account_type'].label = "Second Action In:"


    class Meta:
        model = Order
        fields = ['source_currency_type', 'account_type', 'next_step__account_type', 'time', 'time_lt']
