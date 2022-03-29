from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models.user import User


def validate_staff(value):
    if not value.is_staff:
        raise ValidationError("Staffs can't have wallet")
    return value


# Do I need this model?
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, validators=[validate_staff])


@receiver(post_save, sender=User)
def make_user_staff(sender, instance, **kwargs):
    if instance.is_staff and instance.staff is None:
        staff = Staff.objects.create(user=instance)
        staff.save()
