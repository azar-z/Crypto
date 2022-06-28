import csv
import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Sum
from django.urls import reverse
from django.utils import timezone

import user.validators.user as validators
from user.models.base_model import BaseModel


def get_18_years_ago():
    return timezone.now() + datetime.timedelta(days=-(18 * 365))


class User(AbstractUser, BaseModel):
    CITY_CHOICES = [
        ('TH', 'Tehran'),
        ('ES', 'Esfehan'),
        ('MSH', 'Mashhad'),
        ('SHR', 'Shiraz'),
        ('YZ', 'Yazd'),
    ]
    phone_number = models.CharField(validators=[validators.phone_regex], max_length=17, default='9102164912')
    national_code = models.CharField(max_length=10, validators=[validators.national_code_regex], default='0123456789')
    address = models.CharField(max_length=300, null=True)
    city = models.CharField(choices=CITY_CHOICES, max_length=5, default='TH')
    birthday = models.DateField(default=get_18_years_ago)
    is_woman = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('user_panel')

    def get_total_transaction(self):
        done_orders = self.orders.filter(status__endswith='D')
        return round(done_orders.aggregate(
            sum=Sum(F('source_currency_amount') * F('price'))
        )['sum'] or 0, 2)

    def get_total_profit_or_loss(self):
        two_step_orders = self.orders.filter(previous_step=None).exclude(next_step=None)
        done_two_step_orders = two_step_orders.filter(status__endswith='D').filter(next_step__status__endswith='D')
        total_profit_or_loss = 0
        for order in done_two_step_orders:
            total_profit_or_loss += order.get_profit_or_loss()[0]
        return total_profit_or_loss

    @classmethod
    def export_data(cls):
        with open('exported_data/user_data.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            header = ['id', 'username', 'phone_number', 'national_code', 'address', 'city',
                      'birthday', 'age', 'is_woman',
                      'total_transaction', 'total_transaction_b', 'total_profit_or_loss', 'total_profit_or_loss_b',
                      'total_profit_or_loss_percent']
            writer.writerow(header)
            for user in User.objects.all():
                if not user.is_staff:
                    total_transaction = user.get_total_transaction()
                    total_profit_or_loss = user.get_total_profit_or_loss()
                    total_profit_or_loss_percent = 0
                    if total_transaction != 0:
                        total_profit_or_loss_percent = total_profit_or_loss / total_transaction * 100
                    data = [user.id, user.username, user.phone_number, user.national_code, user.address,
                            user.get_city_display(),
                            user.birthday, user.get_age(), user.is_woman,
                            total_transaction, total_transaction // 10 ** 9,
                            total_profit_or_loss, total_profit_or_loss // 10 ** 9,
                            total_profit_or_loss_percent]
                    writer.writerow(data)

    def get_age(self):
        return timezone.now().year - self.birthday.year

    def send_sms_to_user(self, text):
        data = {
            'receiver': self.phone_number,
            'text': text
        }
        # publish('send_sms', data)


