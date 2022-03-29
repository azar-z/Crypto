from django.contrib.auth.models import AbstractUser
from django.db import models

import user.validators.user as validators
from user.models.base_model import BaseModel


class User(AbstractUser, BaseModel):
    phone_number = models.CharField(validators=[validators.phone_regex], max_length=17, default='9102164912')
    national_code = models.CharField(max_length=10, validators=[validators.national_code_regex], default='0123456789')
    address = models.CharField(max_length=300, null=True)
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True, default='avatar/default_avatar.png')

    # login and signup: inherited from parent
    # adding account: use model forms of accounts
    # delete account: use delete form for account
    # updating profile data: update view
    # see profile data: detail view

    def get_transitions(self):
        pass

    def get_orders(self):
        pass

    def get_accounts(self):
        pass






