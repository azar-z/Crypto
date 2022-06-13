from django.core.exceptions import ValidationError


def validate_staff(user):
    if not user.is_staff:
        raise ValidationError("Only staffs can have staff profile")
    return user
