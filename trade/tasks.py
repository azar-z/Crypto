import datetime

import xlwt
from celery import shared_task

from trade.models import Order


@shared_task
def order_update_status_task():
    Order.update_status_of_all_orders()


@shared_task
def update_golden_trades_task():
    Order.save_golden_trades()


@shared_task
def export_data(export_format, order_ids):
    filename = "tables.xlsx"

    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('Orders')

    row_num = 0

    header_font = xlwt.Font()
    header_font.name = 'Arial'
    header_font.bold = True

    header_style = xlwt.XFStyle()
    header_style.font = header_font

    columns = ['Username', 'Email address',
               'Ordered In', 'Currency',
               'First Action (is_sell)', 'First Action At', 'First Action Amount', 'First Action Price (USDT)',	'First Action Status',
               'Maximum Price (USDT)',	'Minimum Price (USDT)',
               'Second Action (is_sell)',	'Second Action At',	'Second Action Currency Amount', 'Second Action Price (USDT)', 'Second Action Status']

    for col_num in range(len(columns)):
        sheet.write(row_num, col_num, columns[col_num], header_style)

    orders = Order.objects.filter(id__in=order_ids)

    rows = orders.values_list(
        'owner__username', 'owner__email',
        'time', 'source_currency_type',
        'is_sell', 'account_type', 'source_currency_amount', 'price', 'status',
        'max_price', 'min_price',
        'next_step__is_sell', 'next_step__account_type', 'next_step__source_currency_amount', 'next_step__price', 'next_step__status',
    )
    rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime.datetime) else x for x in row] for row in rows]
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            sheet.write(row_num, col_num, row[col_num])

    workbook.save(filename)

    return filename

