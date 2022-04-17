from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.utils.decorators import method_decorator
from django_tables2 import SingleTableView

from trade.models import Order
from trade.tables.transfer_alerts import TransferAlertsTable


@method_decorator(login_required, name='dispatch')
class TransferAlertsView(SingleTableView):
    template_name = 'trade/transfer_alerts.html'
    model = Order
    context_object_name = 'orders'
    table_class = TransferAlertsTable

    def get_queryset(self):
        return self.request.user.orders.filter(status='L').exclude(next_step=None).exclude(account_type=F('next_step__account_type'))

