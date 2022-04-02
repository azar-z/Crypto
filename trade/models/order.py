from django.db import models
from user.models import BaseModel, User
from user.models.account import ACCOUNT_TYPE_CHOICES

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
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=1, choices=ACCOUNT_TYPE_CHOICES)
    status = models.CharField(max_length=1, choices=ORDER_STATUS_CHOICES)
    order_account_id = models.IntegerField()
    source_currency_type = models.CharField(max_length=4, choices=CURRENCIES)
    dest_currency_type = models.CharField(max_length=4, choices=CURRENCIES)
    source_currency_amount = models.DecimalField(max_digits=15, decimal_places=5)
    dest_currency_amount = models.DecimalField(max_digits=15, decimal_places=5)

    def update_status(self):
        pass
    # get data from account and update the status
