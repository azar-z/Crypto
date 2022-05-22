from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django_tables2.export import ExportMixin

from trade.filters.order_record import OrderRecordFilterSet
from trade.models import Order
from trade.tables.order_record import OrderRecordTable
from trade.tasks import export_data


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class DjangoTableOrderRecordView(ExportMixin, SingleTableMixin, FilterView):
    template_name = 'trade/records/django_table_record.html'
    model = Order
    context_object_name = 'orders'
    filterset_class = OrderRecordFilterSet
    table_class = OrderRecordTable
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.select_related('owner').exclude(owner=None).filter(previous_step=None)

    def get(self, request, *args, **kwargs):
        response = super(DjangoTableOrderRecordView, self).get(request, *args, **kwargs)
        if 'export_format' in self.request.GET:
            orders = self.object_list
            order_ids = list(orders.values_list('id', flat=True))
            export_format = self.request.GET['export_format']
            task = export_data.delay(export_format, order_ids)
            response.context_data.update({"task_id": task.task_id})
            return render(request,
                          'trade/records/html_table_record.html',
                          response.context_data
                          )
        return response
