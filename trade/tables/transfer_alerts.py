import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from trade.models import Order


class TransferAlertsTable(tables.Table):
    currency = tables.Column(verbose_name='Currency', accessor='get_transferred_currency')
    account_type = tables.Column(verbose_name='From')
    next_step__account_type = tables.Column(verbose_name='To')
    confirm_or_cancel = tables.Column(verbose_name='', accessor='get_profit_or_loss')
    id = tables.Column(verbose_name='')

    def render_confirm_or_cancel(self, value, record):
        confirm_page = reverse('transfer_request', kwargs={'pk': record.pk})
        confirm_button = "<a class='btn btn-success' href={0}>Confirm</span>".format(confirm_page)
        cancel_page = reverse('transfer_cancel', kwargs={'pk': record.pk})
        cancel_button = "<a class='btn btn-danger' href={0}>Cancel</span>".format(cancel_page)
        return format_html(confirm_button + cancel_button)

    def render_currency(self, value, record):
        return format_html('<span>{0} {1}</span>', value[0], value[1])

    def render_id(self, value, record):
        detail_page = reverse('order_detail', kwargs={'pk': record.pk})
        detail_button = "<a class='btn btn-info' href={0}>Order Details</span>".format(detail_page)
        return format_html(detail_button)

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = ['currency', 'account_type', 'next_step__account_type', 'confirm_or_cancel', 'id']
