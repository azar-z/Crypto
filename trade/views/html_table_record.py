from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django.shortcuts import render

from trade.filters.order_record import OrderRecordFilterSet
from trade.models import Order
from trade.tasks import export_data


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class HTMLOrderRecordView(FilterView):
    template_name = 'trade/records/html_table_record.html'
    model = Order
    context_object_name = 'orders'
    filterset_class = OrderRecordFilterSet
    paginate_by = 7

    def get_queryset(self):
        return Order.objects.select_related('owner').exclude(owner=None).filter(previous_step=None)

    def get(self, request, *args, **kwargs):
        response = super(HTMLOrderRecordView, self).get(request, *args, **kwargs)
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



