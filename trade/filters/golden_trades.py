import django_filters

from trade.models import Order


class GoldenTradesFilterSet(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        super(GoldenTradesFilterSet, self).__init__(*args, **kwargs)
        self.filters['account_type'].label = "First Action In:"
        self.filters['next_step__account_type'].label = "Second Action In:"

    class Meta:
        model = Order
        fields = ['source_currency_type', 'account_type', 'next_step__account_type']
