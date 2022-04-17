import datetime
import os
import random

import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto.settings')
django.setup()

from trade.models import Order
from trade.currencies import SOURCE_CURRENCIES, DEST_CURRENCIES
from user.models.account import ACCOUNT_TYPE_CHOICES
from faker import Faker
from user.models import User
from trade.models.order import ORDER_STATUS_CHOICES

NUM_OF_USERS = 10


def create_users():
    fake = Faker()
    for _ in range(NUM_OF_USERS):
        fake_profile = fake.simple_profile()

        user = User.objects.create(
            username=fake_profile['username'],
            email=fake_profile['mail'],
            national_code=fake.numerify("##########"),
            phone_number=fake.numerify("+##########"),
            address=fake_profile['address'],
            first_name=fake.first_name(),
            last_name=fake.last_name(),
        )
        user.set_password('1234')
        user.save()


def create_orders():
    i = 0
    for _ in range(NUM_OF_USERS):
        i += 1
        while User.objects.get(id=i).is_staff:
            i += 1
        user = User.objects.get(id=i)
        j = random.randint(10, 30)
        for _ in range(j):
            create_one_step_order(owner_id=user.id)
        j = random.randint(10, 30)
        for _ in range(j):
            create_two_step_order(owner_id=user.id)


def create_one_step_order(owner_id):
    fake = Faker()
    first_step_time = fake.date_between_dates(date_start=timezone.now() + datetime.timedelta(days=-60),
                                              date_end=timezone.now())
    order = Order.objects.create(
        owner_id=owner_id,
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
    order.save()


def create_two_step_order(owner_id):
    fake = Faker()
    first_step_time = fake.date_between_dates(date_start=timezone.now() + datetime.timedelta(days=-60),
                                              date_end=timezone.now())
    second_step_time = fake.date_between_dates(first_step_time, date_end=timezone.now())
    second_step = Order.objects.create(
        owner_id=owner_id,
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
    second_step.save()
    first_step_account_type = random.choice(ACCOUNT_TYPE_CHOICES)[0]
    if second_step.status == 'NO':
        first_step_status = random.choice(ORDER_STATUS_CHOICES)[0]
    else:
        if first_step_account_type == second_step.account_type:
            first_step_status = 'OD'
        else:
            first_step_status = 'TD'
    first_step = Order.objects.create(
        owner_id=owner_id,
        status=first_step_status,
        time=first_step_time,
        is_sell=not second_step.is_sell,
        price=random.randint(10, 1000),
        account_type=first_step_account_type,
        id_in_account=fake.numerify("##################"),
        source_currency_type=second_step.source_currency_type,
        dest_currency_type=second_step.dest_currency_type,
        source_currency_amount=round(random.uniform(0.001, 1000.0), 3),
        profit_limit=random.uniform(0.001, 1.0),
        loss_limit=random.uniform(0.001, 1.0),
        deposit_wallet_address=fake.pystr(50, 100),
        withdraw_id=fake.numerify("##################"),
        transfer_fee=round(random.uniform(0.01, 10.0), 3),
        next_step=second_step
    )
    first_step.save()


if __name__ == "__main__":
    create_users()
    create_orders()

'''
    owner = ,
    status =,
    time = ,
    is_sell =, 
    price = ,
    account_type = ,
    id_in_account = ,
    source_currency_type = ,
    dest_currency_type = ,
    source_currency_amount =, 
    profit_limit = ,
    got_to_profit_limit =, 
    loss_limit = ,
    got_to_loss_limit =,
    deposit_wallet_address = ,
    withdraw_id = ,
    transfer_fee = ,
    next_step = 
    
'''
