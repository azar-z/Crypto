from django.db import models
from user.models import BaseModel, User
from user.models.account import ACCOUNT_TYPE_CHOICES, Account

CURRENCIES = (
    ('IRR', 'Iran Rial'),
    ('BTC', 'Bitcoin'),
    ('BTH', 'Bitcoin Cash'),
    ('ETH', 'Ethereum'),
    ('ETC', 'Ethereum Classic'),
    ('USDT', 'Tether'),
)

ORDER_STATUS_CHOICES = (
    ('A', 'active'),
    ('D', 'done'),
    ('C', 'cancelled'),
    ('E', 'expired'),
)


class Order(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=ORDER_STATUS_CHOICES)
    order_id_in_account = models.IntegerField()
    source_currency_type = models.CharField(max_length=4, choices=CURRENCIES)
    dest_currency_type = models.CharField(max_length=4, choices=CURRENCIES)
    source_currency_amount = models.DecimalField(max_digits=15, decimal_places=5)
    dest_currency_amount = models.DecimalField(max_digits=15, decimal_places=5)

    def update_status(self):
        pass
    # get data from account and update the status
