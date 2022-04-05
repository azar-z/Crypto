from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from user.models import BaseModel, User
from user.models.account import ACCOUNT_TYPE_CHOICES

SOURCE_CURRENCIES = (
    ('BTC', 'Bitcoin'),
    ('BTH', 'Bitcoin Cash'),
    ('ETH', 'Ethereum'),
    ('ETC', 'Ethereum Classic'),
    ('USDT', 'Tether'),
)
DEST_CURRENCIES = (
    ('IRR', 'Iran Rial'),
)

ORDER_STATUS_CHOICES = (
    ('A', 'active'),
    ('D', 'done'),
    ('C', 'cancelled'),
    ('E', 'expired'),
)

# source = BTC
# dest = IRR


class Order(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    first_step_account_type = models.CharField(choices=ACCOUNT_TYPE_CHOICES, max_length=2)
    first_step_id_in_account = models.CharField(default='0', max_length=100)
    source_currency_type = models.CharField(max_length=4, choices=SOURCE_CURRENCIES)
    dest_currency_type = models.CharField(max_length=4, choices=DEST_CURRENCIES)
    source_currency_amount = models.DecimalField(max_digits=15, decimal_places=5)
    price = models.IntegerField()
    is_sell = models.BooleanField(default=False)
    profit_limit = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    loss_limit = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    got_to_profit_limit = models.BooleanField(default=False)
    got_to_loss_limit = models.BooleanField(default=False)
    second_step_account_type = models.CharField(choices=ACCOUNT_TYPE_CHOICES, max_length=2)
    second_step_id_in_account = models.CharField(default='0', max_length=100)

    def update_status(self):
        pass
    # get data from account and update the status
    # should check for all owner accounts order books to find out if limits are conquered

    def go_to_second_step(self):
        pass
    # order a new trade in a suitable account based on loss or profit limit

    def ready_for_second_step(self):
        return self.got_to_loss_limit or self.got_to_profit_limit

    # update_status -> if ready_for_second_step -> go_to_second_step
