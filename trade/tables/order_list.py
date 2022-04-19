from django.urls import reverse
from django.utils.html import format_html
import django_tables2 as tables

from trade.models import Order


class OrderDataTable(tables.Table):
    source_currency_amount = tables.Column(verbose_name='Currency')
    price = tables.Column(verbose_name='Price')
    is_sell = tables.Column(verbose_name='Actions')
    id = tables.Column(verbose_name='')
    time = tables.Column(verbose_name='Ordered In')
    account_type = tables.Column(verbose_name='First Action At')
    next_step__account_type = tables.Column(verbose_name='Second Action At')
    status = tables.Column(verbose_name='First Action Status')
    next_step__status = tables.Column(verbose_name='Second Action Status')

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
        if value:
            first = sell
            second = buy
        else:
            first = buy
            second = sell
        if record.has_next_step():
            result = first + ' then ' + second
        else:
            result = first
        return format_html(result)

    def render_next_step__account_type(self, value, record):
        return record.next_step.get_account_type_display()

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = ['time', 'source_currency_amount', 'price', 'is_sell', 'account_type',
                  'next_step__account_type', 'status', 'next_step__status', 'id']

