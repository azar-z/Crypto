import datetime
import os
import random

import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto.settings')
django.setup()

from trade.models import Order
from trade.models.order import SOURCE_CURRENCIES, DEST_CURRENCIES
from user.models.account import ACCOUNT_TYPE_CHOICES
from faker import Faker
from user.models import User, Nobitex, Wallex, Exir

NUM_OF_USERS = 10


def create_users():
    fake = Faker()
    for _ in range(NUM_OF_USERS):
        fake_profile = fake.simple_profile()

        user = User.objects.create(
            username=fake_profile['username'],
            password='1234',
            email=fake_profile['mail'],
            national_code=fake.numerify("##########"),
            phone_number=fake.numerify("+##########"),
            address=fake_profile['address'],
            first_name=fake.first_name(),
            last_name=fake.last_name(),
        )
        user.save()


def create_nobitex_account():
    fake = Faker()
    i = 0
    for _ in range(NUM_OF_USERS):
        i += 1
        while User.objects.get(id=i).is_staff:
            i += 1
        account = Nobitex.objects.create(
            token=fake.pystr(max_chars=50),
            email=fake.email(),
            token_expire_time=fake.date_between(),
            owner_id=i
        )
        account.save()


def create_wallex_account():
    fake = Faker()
    i = 0
    for _ in range(NUM_OF_USERS):
        i += 1
        while User.objects.get(id=i).is_staff:
            i += 1
        account = Wallex.objects.create(
            token=fake.pystr(max_chars=50),
            token_expire_time=fake.date_between(),
            owner_id=i
        )
        account.save()


def create_exir_account():
    fake = Faker()
    i = 0
    for _ in range(NUM_OF_USERS):
        i += 1
        while User.objects.get(id=i).is_staff:
            i += 1
        account = Exir.objects.create(
            api_key=fake.pystr(max_chars=50),
            api_signature=fake.pystr(max_chars=50),
            api_expires=fake.pystr(max_chars=50),
            owner_id=i,
            api_key_expire_time=datetime.timedelta(days=30) + timezone.now()
        )
        account.save()


def create_orders():
    i = 0
    for _ in range(NUM_OF_USERS):
        i += 1
        while User.objects.get(id=i).is_staff:
            i += 1
        user = User.objects.get(id=i)
        j = random.randint(1, 5)
        for _ in range(j):
            create_fake_order(owner_id=user.id)


def create_fake_order(owner_id):
    fake = Faker()
    order = Order.objects.create(
        owner_id=owner_id,
        first_step_account_type=random.choice(ACCOUNT_TYPE_CHOICES)[0],
        first_step_id_in_account=fake.pystr(max_chars=100),
        source_currency_type=random.choice(SOURCE_CURRENCIES)[0],
        dest_currency_type=random.choice(DEST_CURRENCIES)[0],
        source_currency_amount=round(random.uniform(0.001, 1000.0), 3),
        price=random.randint(1000, 1000000000),
        is_sell=bool(random.getrandbits(1)),
        profit_limit=random.uniform(0.00001, 1.0),
        loss_limit=random.uniform(0.00001, 1.0),
        got_to_profit_limit=bool(random.getrandbits(1)),
        got_to_loss_limit=bool(random.getrandbits(1)),
        second_step_account_type=random.choice(ACCOUNT_TYPE_CHOICES)[0],
        second_step_id_in_account=fake.pystr(max_chars=100),

    )
    order.save()


if __name__ == "__main__":
    create_users()
    create_nobitex_account()
    create_wallex_account()
    create_exir_account()
    create_orders()
