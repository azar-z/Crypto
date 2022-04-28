from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

import user.validators.user as validators
from user.models.base_model import BaseModel


class User(AbstractUser, BaseModel):
    phone_number = models.CharField(validators=[validators.phone_regex], max_length=17, default='9102164912')
    national_code = models.CharField(max_length=10, validators=[validators.national_code_regex], default='0123456789')
    address = models.CharField(max_length=300, null=True)

    def get_absolute_url(self):
        return reverse('user_panel')

    def send_sms_to_user(self, text):
        data = {
            'receiver': self.phone_number,
            'text': text
        }
        # publish('send_sms', data)

