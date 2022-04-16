from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from trade.filters.order_list_filter import OrderListFilterSet
from trade.models import Order
from trade.tables.order_list import OrderDataTable


@method_decorator(login_required, name='dispatch')
class OrderListView(SingleTableMixin, FilterView):
    template_name = 'trade/order_list.html'
    model = Order
    context_object_name = 'orders'
    table_class = OrderDataTable
    filterset_class = OrderListFilterSet

    def get_queryset(self):
        return self.request.user.orders.all()
