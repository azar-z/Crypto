from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models import User, Account


@receiver(post_save, sender=User)
def make_accounts(sender, instance, created, **kwargs):
    if created and not instance.is_staff:
        for subclass in Account.__subclasses__():
            subclass.make_an_account_for_user(instance)
