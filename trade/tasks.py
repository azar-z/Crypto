from celery import shared_task

from trade.models import Order
from user.errors import NoAuthenticationInformation


@shared_task
def order_os_to_od_task():
    orders = Order.objects.filter(status='OS')
    for order in orders:
        try:
            order.check_for_order_status()
        except NoAuthenticationInformation:
            pass


@shared_task
def order_od_to_l_to_next_step_os_task():
    orders = Order.objects.filter(status='OD')
    for order in orders:
        if order.has_next_step():
            try:
                got_to_limit = order.check_for_profit_or_loss_limits()
                if got_to_limit and not order.needs_transfer():
                    order.next_step.order_transaction()
            except NoAuthenticationInformation:
                pass


@shared_task
def order_tos_to_td_to_next_step_os_task():
    orders = Order.objects.filter(status='TOS')
    for order in orders:
        if order.has_next_step():
            try:
                transfer_done = order.next_step.check_for_enough_balance()
                if transfer_done:
                    order.status = 'TD'
                    order.save()
                    order.next_step.order_transaction()
            except NoAuthenticationInformation:
                pass
