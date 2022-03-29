from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models.staff import Staff
from user.models.user import User

