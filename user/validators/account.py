from django.core.exceptions import ValidationError

from user.models import User


def validate_not_staff(user_id):
    user = User.objects.get(id=user_id)
    if user.is_staff:
        raise ValidationError("Staffs can't have accounts")
    return user
