import os
import random

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto.settings')
django.setup()

from user.models import User
from trade.fake_data_utils import create_one_step_order, create_two_step_order
from user.fake_data_utils import create_fake_user

NUM_OF_USERS = 10


def create_users():
    for _ in range(NUM_OF_USERS):
        create_fake_user()


def create_orders():
    i = 0
    for _ in range(NUM_OF_USERS):
        i += 1
        while User.objects.get(id=i).is_staff:
            i += 1
        user = User.objects.get(id=i)
        j = random.randint(10, 30)
        for _ in range(j):
            create_one_step_order(owner=user)
        j = random.randint(10, 30)
        for _ in range(j):
            create_two_step_order(owner=user)


if __name__ == "__main__":
    create_users()
    create_orders()

