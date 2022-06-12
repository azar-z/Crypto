import datetime
import random

from django.utils.timezone import make_aware
from django.utils import timezone
from faker import Faker

from trade.models import Order
from trade.models.order import ORDER_STATUS_CHOICES
from trade.utils import SOURCE_CURRENCIES, DEST_CURRENCIES
from user.models.account import ACCOUNT_TYPE_CHOICES


def get_aware_datetime(date):
    datetime_object = datetime.datetime.combine(date, datetime.datetime.min.time())
    return make_aware(datetime_object)


def create_one_step_order(owner):
    fake = Faker()
    first_step_time = fake.date_between_dates(date_start=timezone.now() + datetime.timedelta(days=-60),
                                              date_end=timezone.now())
    first_step_time = get_aware_datetime(first_step_time)
    order = Order.objects.create(
        owner=owner,
        status=random.choice(ORDER_STATUS_CHOICES)[0],
        time=first_step_time,
        is_sell=bool(random.getrandbits(1)),
        price=random.randint(10, 10000000),
        account_type=random.choice(ACCOUNT_TYPE_CHOICES)[0],
        id_in_account=fake.numerify("##################"),
        source_currency_type=random.choice(SOURCE_CURRENCIES)[0],
        dest_currency_type=random.choice(DEST_CURRENCIES)[0],
        source_currency_amount=round(random.uniform(0.001, 1000.0), 3),
    )
    order.add_tag(fake.pystr(10, 20))
    order.save()
    return order


def create_two_step_order(owner):
    fake = Faker()
    first_step_time = fake.date_between_dates(date_start=timezone.now() + datetime.timedelta(days=-60),
                                              date_end=timezone.now())
    second_step_time = fake.date_between_dates(first_step_time, date_end=timezone.now())
    first_step_time = get_aware_datetime(first_step_time)
    second_step_time = get_aware_datetime(second_step_time)
    second_step = Order.objects.create(
        owner=owner,
        status=random.choice(ORDER_STATUS_CHOICES)[0],
        time=second_step_time,
        is_sell=bool(random.getrandbits(1)),
        price=random.randint(10, 10000000),
        account_type=random.choice(ACCOUNT_TYPE_CHOICES)[0],
        id_in_account=fake.numerify("##################"),
        source_currency_type=random.choice(SOURCE_CURRENCIES)[0],
        dest_currency_type=random.choice(DEST_CURRENCIES)[0],
        source_currency_amount=round(random.uniform(0.001, 1000.0), 3)
    )
    second_step.add_tag(fake.pystr(10, 20))
    second_step.save()
    first_step_account_type = random.choice(ACCOUNT_TYPE_CHOICES)[0]
    if second_step.status == 'NO':
        first_step_status = random.choice(ORDER_STATUS_CHOICES)[0]
    else:
        if first_step_account_type == second_step.account_type:
            first_step_status = 'OD'
        else:
            first_step_status = 'TD'
    price = random.randint(10, 1000)
    max_price = random.randint(price, 1000)
    min_price = random.randint(10, price)
    first_step = Order.objects.create(
        owner=owner,
        status=first_step_status,
        time=first_step_time,
        is_sell=not second_step.is_sell,
        price=price,
        account_type=first_step_account_type,
        id_in_account=fake.numerify("##################"),
        source_currency_type=second_step.source_currency_type,
        dest_currency_type=second_step.dest_currency_type,
        source_currency_amount=round(random.uniform(0.001, 1000.0), 3),
        max_price=max_price,
        min_price=min_price,
        deposit_wallet_address=fake.pystr(50, 100),
        withdraw_id=fake.numerify("##################"),
        transfer_fee=round(random.uniform(0.01, 10.0), 3),
        next_step=second_step
    )
    first_step.add_tag(fake.pystr(10, 20))
    first_step.save()
    return first_step
