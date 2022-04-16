from django.urls import reverse
from django.utils.html import format_html
import django_tables2 as tables

from trade.models import Order


class OrderDataTable(tables.Table):
    source_currency_amount = tables.Column(verbose_name='Currency')
    price = tables.Column(verbose_name='Price')
    is_sell = tables.Column(verbose_name='Action To Currency')
    id = tables.Column(verbose_name='')
    created = tables.Column(verbose_name='Ordered At')

    def render_id(self, value, record):
        href = reverse('order_detail', kwargs={'pk': value})
        return format_html('<a class="btn btn-info" href="{0}">Details</a>', href)

    def render_source_currency_amount(self, value, record):
        return format_html('<span>{0} {1}</span>', value, record.source_currency_type)

    def render_price(self, value, record):
        return format_html('<span>{0} {1}</span>', value, record.dest_currency_type)

    def render_is_sell(self, value, record):
        buy = '<span class="table-success">buy</span>'
        sell = '<span class="table-danger">sell</span>'
        result = '-'
        if record.has_second_step:
            if not value:
                result = buy + ' then ' + sell
        else:
            if value:
                result = sell
            else:
                result = buy
        return format_html(result)

    def render_second_step_account_type(self, value, record):
        if record.has_second_step:
            return '-'
        else:
            return value

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = ['created', 'source_currency_amount', 'price', 'is_sell', 'first_step_account_type',
                  'second_step_account_type', 'status', 'id']

