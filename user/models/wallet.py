from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models.user import User

WALLET_TYPE_CHOICES = (
    ('N', "Nobitex"),
    ('W', "Wallex"),
)


def validate_not_staff(value):
    if value.is_staff:
        raise ValidationError("Staffs can't have wallet")
    return value


class Wallet(models.Model):
    is_default = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, validators=[validate_not_staff])
    type = models.CharField(max_length=1, choices=WALLET_TYPE_CHOICES)
    added_date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    password = models.CharField(max_length=200)  # how to secure it?


# method or signal?
@receiver(post_save, sender=Wallet)
def make_wallet_default(sender, instance, *args, **kwargs):
    if instance.is_default:
        for wallet in instance.owner.wallets.all():
            if wallet is not instance:
                wallet.is_default = False
