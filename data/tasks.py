from celery import shared_task

from data.models import CryptoPrice
from user.models import User


@shared_task
def export_user_data_task():
    User.export_data()


@shared_task
def export_price_data_task():
    CryptoPrice.export_data()


@shared_task
def save_prices_task():
    CryptoPrice.save_prices()
