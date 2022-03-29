from user.models.user import User


class Staff(User):
    class Meta:
        proxy = True

