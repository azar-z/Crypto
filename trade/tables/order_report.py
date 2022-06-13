from django.utils.html import format_html
import django_tables2 as tables

from trade.models import Order

buy = '<span class="table-success">Buy</span>'
sell = '<span class="table-danger">Sell</span>'


def get_action_value_rendered(is_sell):
    if is_sell:
        return format_html(sell)
    return format_html(buy)

class OrderRecordTable(tables.Table):
    source_currency_type = tables.Column(verbose_name='Currency')
    time = tables.Column(verbose_name='Ordered In')
    is_sell = tables.Column(verbose_name='First Action')
    source_currency_amount = tables.Column(verbose_name='First Action Amount')
    account_type = tables.Column(verbose_name='First Action At')
    status = tables.Column(verbose_name='First Action Status')
    price = tables.Column(verbose_name='First Action Price (USDT)')
    next_step__is_sell = tables.Column(verbose_name='Second Action')
    next_step__account_type = tables.Column(verbose_name='Second Action At')
    next_step__status = tables.Column(verbose_name='Second Action Status')
    next_step__price = tables.Column(verbose_name='Second Action Price (USDT)')
    next_step__source_currency_amount = tables.Column(verbose_name='Second Action Currency Amount')


    def render_is_sell(self, value, record):
        return get_action_value_rendered(value)

    def render_next_step__is_sell(self, value, record):
        return get_action_value_rendered(value)

    def render_time(self, value, record):
        return value.date

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = ['owner__username', 'owner__email',
                  'time', 'source_currency_type',
                  'is_sell', 'account_type', 'source_currency_amount', 'price', 'status',
                  'max_price', 'min_price',
                  'next_step__is_sell', 'next_step__account_type', 'next_step__source_currency_amount', 'next_step__price', 'next_step__status']

