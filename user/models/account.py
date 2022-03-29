from django.db import models

from user.models.base_model import BaseModel
from user.models.user import User
import user.validators.account as validators

Account_TYPE_CHOICES = (
    ('N', "Nobitex"),
    ('W', "Wallex"),
    ('E', "Exir"),
)


class Account(BaseModel):
    _was_default = False
    is_default = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, validators=[validators.validate_not_staff],
                              related_name='%(class)s_accounts')
    type = models.CharField(max_length=1, choices=Account_TYPE_CHOICES)

    def save(self, *args, **kwargs):
        if self.is_default and not self._was_default:
            self.set_as_default()
            self._was_default = True
        super(Account, self).save(*args, **kwargs)

    @classmethod
    def get_orderbook(cls, source='BTC', dest='IRR'):
        pass

    @classmethod
    def get_trades(cls, source='BTC', dest='IRR'):
        pass

    def set_as_default(self):
        print('set is default runs')
        for account in self.owner.nobitex_accounts.all():
            if account is not self:
                account.is_default = False
                account.save()
        for account in self.owner.wallex_accounts.all():
            if account is not self:
                account.is_default = False
                account.save()
        for account in self.owner.exir_accounts.all():
            if account is not self:
                account.is_default = False
                account.save()
        self.is_default = True

    def new_order(self, source, dest, amount, price):
        pass

    def cancel_order(self, order):
        pass

    def get_inventory(self, currency):
        pass

    def logout(self):
        pass

    def has_authentication_information(self):
        pass
        # boolean output

    def get_authentication_information(self):
        pass

    def get_wallets(self):
        pass

    class Meta:
        abstract = True


class Nobitex(Account):
    token = models.CharField(max_length=100)
    email = models.EmailField()

    def get_token(self, email, password):
        pass # throw login


class Wallex(Account):
    token = models.CharField(max_length=100)
    token_expire_time = models.DateTimeField()

    def get_token(self, email, password):
        pass # throw user, set expire date
    # WebSocket?


class Exir(Account):
    api_key = models.CharField(max_length=200)
    api_signature = models.CharField(max_length=200)
    api_expires = models.CharField(max_length=200)
