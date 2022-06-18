import datetime
import random

from django.utils import timezone
from faker import Faker

from user.models import User


def create_fake_user():
    fake = Faker()
    birthday = fake.date_between_dates(date_start=timezone.now() + datetime.timedelta(days=-(70 * 365)),
                                       date_end=timezone.now() + datetime.timedelta(days=-(18 * 365)))
    fake_profile = fake.simple_profile()
    while User.objects.filter(username=fake_profile['username']).count() != 0:
        fake_profile = fake.simple_profile()
    user = User.objects.create(
        username=fake_profile['username'],
        email=fake_profile['mail'],
        national_code=fake.numerify("##########"),
        phone_number=fake.numerify("+##########"),
        address=fake_profile['address'],
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        birthday=birthday,
        is_woman=bool(random.getrandbits(1)),
        city=random.choice(User.CITY_CHOICES)[0],
    )
    user.set_password('1234')
    user.add_tag(fake.pystr(10, 20))
    user.add_tag(fake.pystr(10, 20))
    user.save()
    return user

