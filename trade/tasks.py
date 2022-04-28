from celery import shared_task

from trade.models import Order


@shared_task
def order_update_status_task():
    Order.update_status_of_all_orders()


@shared_task
def update_golden_trades_task():
    Order.save_golden_trades()
