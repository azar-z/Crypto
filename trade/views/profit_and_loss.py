from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_tables2 import SingleTableMixin
from django_filters import views as filter_views

from trade.filters.profit_and_loss_filter import ProfitAndLossFilterSet
from trade.models import Order
from trade.tables.profit_and_loss import OrderProfitAndLossTable


@method_decorator(login_required, name='dispatch')
class ProfitAndLossView(SingleTableMixin, filter_views.FilterView):
    template_name = 'trade/profit_and_loss.html'
    model = Order
    context_object_name = 'orders'
    filterset_class = ProfitAndLossFilterSet
    table_class = OrderProfitAndLossTable

    def get_queryset(self):
        current_user = self.request.user
        return current_user.orders.exclude(status='NO').filter(previous_step=None)

