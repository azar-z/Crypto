from django.contrib.auth.forms import UserCreationForm

from user.models import User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number', 'national_code', 'address')
