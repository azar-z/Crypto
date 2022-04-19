import json

import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html

from trade.models import Order

def get_html_format_of_action(is_sell):
    if is_sell:
        result = '<span class="table-danger">sell</span>'
    else:
        result = '<span class="table-success">buy</span>'
    return format_html(result)


class GoldenTradesTable(tables.Table):
    is_sell = tables.Column(verbose_name='First Action')
    next_step__is_sell = tables.Column(verbose_name='Second Action')
    price = tables.Column(verbose_name='With price (USDT)')
    next_step__price = tables.Column(verbose_name='With price (USDT)')
    next_step__account_type = tables.Column(verbose_name='In')
    profit_limit = tables.Column(verbose_name='Profit')
    accept = tables.Column(verbose_name='', accessor='get_form_initials')

    def render_accept(self, value, record):
        data = json.dumps(value)
        href = "{0}?initial={1}".format(reverse('new_trade'), data)
        return format_html('<a class="btn btn-info" href="{0}">Accept</a>', href)

    def render_is_sell(self, value, record):
        return get_html_format_of_action(value)

    def render_next_step__is_sell(self, value, record):
        return get_html_format_of_action(value)

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = ['source_currency_type', 'is_sell', 'account_type', 'price',
                  'next_step__is_sell', 'next_step__account_type', 'next_step__price', 'profit_limit',
                  'accept']
