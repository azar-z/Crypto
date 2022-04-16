import django_tables2 as tables
from django.utils.html import format_html

from trade.models import Order


def get_style_class(value):
    if value < 0:
        style_class = 'table-danger'
    elif value == 0:
        style_class = 'table-warning'
    else:
        style_class = 'table-success'
    return style_class


def sum_footer(table):
    s = sum(x.get_profit_or_loss() for x in table.data)
    return format_html("<span class='{0}'>{1} {2}</span>", get_style_class(s), s, 'IRR')


class OrderProfitAndLossTable(tables.Table):
    source_currency_amount = tables.Column(verbose_name='Source Currency', footer='Total:')
    price = tables.Column(verbose_name='Buy Price')
    second_step_price = tables.Column(verbose_name='Sell Price')
    profit_or_loss = tables.Column(verbose_name='Profit Or Loss', accessor='get_profit_or_loss', footer=sum_footer)

    def render_profit_or_loss(self, value, record):
        return format_html("<span class='{0}'>{1} {2}</span>", get_style_class(value), value, record.dest_currency_type)

    def render_source_currency_amount(self, value, record):
        return format_html('<span>{0} {1}</span>', value, record.source_currency_type)

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = ['source_currency_amount', 'price', 'second_step_price', 'profit_or_loss']
