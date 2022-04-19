import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html

from trade.models import Order


def get_style_class(value):
    if value < 0:
        style_class = 'table-danger'
    elif value == 0:
        style_class = ''
    else:
        style_class = 'table-success'
    return style_class


def sum_footer(table):
    s = sum(x.get_profit_or_loss()[0] for x in table.data if x.has_next_step() and not x.is_sell)
    return format_html("<span class='{0}'>{1} {2}</span>", get_style_class(s), s, 'USDT')


class OrderProfitAndLossTable(tables.Table):
    source_currency_amount = tables.Column(verbose_name='Currency',
                                           footer='Total:')
    price = tables.Column(verbose_name='Primary Price')
    next_step__price = tables.Column(verbose_name='Secondary Price')
    profit_or_loss = tables.Column(verbose_name='Profit Or Loss', accessor='get_profit_or_loss', footer=sum_footer)
    is_sell = tables.Column(verbose_name='Action')
    id = tables.Column(verbose_name='')

    def render_id(self, value, record):
        href = reverse('order_detail', kwargs={'pk': value})
        return format_html('<a class="btn btn-info" href="{0}">Details</a>', href)

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

    def render_profit_or_loss(self, value, record):
        profit_or_loss = value[0]
        currency_type = value[1]
        return format_html("<span class='{0}'>{1} {2}</span>", get_style_class(profit_or_loss), profit_or_loss,
                           currency_type)

    def render_source_currency_amount(self, value, record):
        return format_html('<span>{0} {1}</span>', value, record.source_currency_type)

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = ['source_currency_amount', 'is_sell', 'price', 'next_step__price', 'profit_or_loss', 'id']
