import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from trade.models import Order


class TransferAlertsTable(tables.Table):
    source_currency_amount = tables.Column(verbose_name='Currency')
    second_step_price = tables.Column(verbose_name='Sell Price')
    first_step_account_type = tables.Column(verbose_name='From')
    second_step_account_type = tables.Column(verbose_name='To')
    confirm_or_cancel = tables.Column(verbose_name='', accessor='get_profit_or_loss')

    def render_confirm_or_cancel(self, value, record):
        confirm_page = reverse('transfer_request', kwargs={'pk': record.pk})
        confirm_button = "<a class='btn btn-success' href={0}>Confirm</span>".format(confirm_page)
        cancel_page = reverse('transfer_cancel', kwargs={'pk': record.pk})
        cancel_button = "<a class='btn btn-danger' href={0}>Cancel</span>".format(cancel_page)
        return format_html(confirm_button + cancel_button)

    def render_source_currency_amount(self, value, record):
        return format_html('<span>{0} {1}</span>', value, record.source_currency_type)

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = ['source_currency_amount', 'second_step_price', 'first_step_account_type',
                  'second_step_account_type', 'confirm_or_cancel']
