import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto.settings')
django.setup()

from faker import Faker

from user.models import User, Nobitex, Wallex, Exir

NUM_OF_USERS = 10


def create_users():
    fake = Faker()
    for _ in range(NUM_OF_USERS):
        user = User.objects.create(
            username=fake.name(),
            national_code=fake.numerify("##########"),
            phone_number=fake.numerify("+##########"),
            address=fake.address()
        )
        user.set_password("1234")
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
            owner_id=i
        )
        account.save()


if __name__ == "__main__":
    create_users()
    create_nobitex_account()
    create_wallex_account()
    create_exir_account()
