import csv
import datetime
from decimal import Decimal

from django.db import models
from django.utils import timezone

from data.utils import get_price_data_file_name
from trade.utils import SOURCE_CURRENCIES
from user.logics.accounts import get_account_class_based_on_type
from user.models.account import ACCOUNT_TYPE_CHOICES


class CryptoPrice(models.Model):
    currency = models.CharField(verbose_name='Currency', max_length=4, choices=SOURCE_CURRENCIES)
    highest_price = models.DecimalField(verbose_name='Highest Price (USDT)', max_digits=20, decimal_places=2, default=0)
    lowest_price = models.DecimalField(verbose_name='Lowest Price (USDT)', max_digits=20, decimal_places=2, default=0)
    account_type = models.CharField(verbose_name='In', choices=ACCOUNT_TYPE_CHOICES, max_length=2)
    time = models.DateTimeField(default=timezone.now)

    @classmethod
    def export_data(cls):
        for account_type in ACCOUNT_TYPE_CHOICES:
            account_type = account_type[0]
            for currency in SOURCE_CURRENCIES:
                currency = currency[0]
                cls._export_data(currency, account_type)

    @classmethod
    def _export_data(cls, currency, account_type):
        with open(get_price_data_file_name(currency, account_type), 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            header = ['time', 'highest_price', 'lowest_price']
            writer.writerow(header)
            prices = cls.objects.filter(currency=currency, account_type=account_type)
            rows = prices.values_list('time', 'highest_price', 'lowest_price')
            rows = [[x.strftime("%Y-%m-%d %H:%M:%S") if isinstance(x, datetime.datetime) else x for x in row]
                    for row in rows]
            for row in rows:
                writer.writerow(row)

    @classmethod
    def save_prices(cls):
        for account_type in ACCOUNT_TYPE_CHOICES:
            account_type = account_type[0]
            for currency in SOURCE_CURRENCIES:
                currency = currency[0]
                cls.save_price(currency, account_type)

    @classmethod
    def save_price(cls, currency, account_type):
        account = get_account_class_based_on_type(account_type)
        market_info = account.get_market_info(currency, 'USDT')
        price_obj = cls.objects.create(currency=currency, account_type=account_type,
                                       highest_price=Decimal(market_info['bestSell']),
                                       lowest_price=Decimal(market_info['bestBuy']))
        price_obj.save()
