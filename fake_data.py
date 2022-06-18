import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto.settings')
django.setup()

from user.models import User
from trade.fake_data_utils import create_one_step_order, create_two_step_order
from user.fake_data_utils import create_fake_user

NUM_OF_USERS = 300
NUM_OF_ORDERS = 30

def create_users():
    for _ in range(NUM_OF_USERS):
        create_fake_user()


def create_orders():
    i = 0
    for user in User.objects.all():
        if not user.is_staff:
            for _ in range(NUM_OF_ORDERS):
                create_one_step_order(owner=user)
            for _ in range(NUM_OF_ORDERS):
                create_two_step_order(owner=user)


if __name__ == "__main__":
    create_users()
    create_orders()

