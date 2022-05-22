import django_filters
from bootstrap_datepicker_plus.widgets import DateTimePickerInput

from trade.models import Order

FILTER_CHOICES = (
    (True, 'Sell'),
    (False, 'Buy'),
)

class OrderRecordFilterSet(django_filters.FilterSet):
    time = django_filters.DateTimeFilter(label='From', widget=DateTimePickerInput(), lookup_expr='gt')
    time_lt = django_filters.DateTimeFilter(field_name='time', label='Till', widget=DateTimePickerInput(), lookup_expr='lt')
    owner__username = django_filters.CharFilter(lookup_expr='icontains')
    owner__email = django_filters.CharFilter(lookup_expr='icontains')
    is_sell = django_filters.ChoiceFilter(choices=FILTER_CHOICES)
    next_step__is_sell = django_filters.ChoiceFilter(choices=FILTER_CHOICES)

    def __init__(self, *args, **kwargs):
        super(OrderRecordFilterSet, self).__init__(*args, **kwargs)
        self.filters['account_type'].label = "First Action In:"
        self.filters['next_step__account_type'].label = "Second Action In:"
        self.filters['status'].label = "First Action Status:"
        self.filters['next_step__status'].label = "Second Action Status:"
        self.filters['is_sell'].label = "First Action:"
        self.filters['next_step__is_sell'].label = "Second Action:"

    class Meta:
        model = Order
        fields = ['owner__username', 'owner__email',
                  'source_currency_type',
                  'account_type', 'next_step__account_type',
                  'time', 'time_lt',
                  'is_sell', 'next_step__is_sell',
                  'status', 'next_step__status',
                  ]
