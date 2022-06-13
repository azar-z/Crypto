import requests
from celery import shared_task
from django.core.cache import cache

from trade.utils import SOURCE_CURRENCIES, DEST_CURRENCIES
from user.models import Wallex


@shared_task
def _cache_orderbook_task(market_symbol):
    url = "https://api.wallex.ir/v1/depth?symbol=" + market_symbol
    value = requests.get(url).json()
    cache_key = 'wallex_orderbook_' + market_symbol
    cache.set(cache_key, value)


@shared_task
def cache_orderbook_task():
    for source_currency in SOURCE_CURRENCIES:
        source = source_currency[0]
        for dest_currency in DEST_CURRENCIES:
            dest = dest_currency[0]
            market_symbol = Wallex.get_market_symbol(source, dest)
            _cache_orderbook_task.delay(market_symbol)


@shared_task
def _cache_trades_task(market_symbol):
    url = "https://api.wallex.ir/v1/trades?symbol=" + market_symbol
    value = requests.get(url).json()
    cache_key = 'wallex_trades_' + market_symbol
    cache.set(cache_key, value)


@shared_task
def cache_trades_task():
    for source_currency in SOURCE_CURRENCIES:
        source = source_currency[0]
        for dest_currency in DEST_CURRENCIES:
            dest = dest_currency[0]
            market_symbol = Wallex.get_market_symbol(source, dest)
            _cache_trades_task.delay(market_symbol)


@shared_task
def cache_market_info_task():
    url = 'https://api.wallex.ir/v1/markets'
    value = requests.get(url).json()
    cache_key = 'wallex_market'
    cache.set(cache_key, value)
