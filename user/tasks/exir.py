import requests
from celery import shared_task
from django.core.cache import cache


@shared_task
def cache_orderbook_task():
    url = "https://api.exir.io/v1/orderbooks"
    value = requests.get(url).json()
    cache_key = 'exir_orderbook'
    cache.set(cache_key, value)


@shared_task
def cache_trades_task():
    url = "https://api.exir.io/v1/trades"
    value = requests.get(url).json()
    cache_key = 'exir_tasks'
    cache.set(cache_key, value)
