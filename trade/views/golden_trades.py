from django_tables2 import SingleTableMixin
from django_filters import views as filter_views

from trade.filters.golden_trades import GoldenTradesFilterSet
from trade.logics.golden_trades import get_statistical_data
from trade.models import Order
from trade.tables.golden_trades import GoldenTradesTable


class GoldenTrades(SingleTableMixin, filter_views.FilterView):
    template_name = 'trade/golden_trades.html'
    model = Order
    context_object_name = 'orders'
    filterset_class = GoldenTradesFilterSet
    table_class = GoldenTradesTable

    def get_queryset(self):
        return Order.objects.filter(owner=None).filter(previous_step=None)

    def get_context_data(self, **kwargs):
        context = super(GoldenTrades, self).get_context_data(**kwargs)
        additional_context = get_statistical_data()
        context.update(additional_context)
        return context
