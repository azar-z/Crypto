from faker import Faker

from user.models import User


def create_fake_user():
    fake = Faker()
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
    user.add_tag(fake.pystr(10, 20))
    user.save()
    return user

