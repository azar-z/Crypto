from django.contrib.auth.forms import UserCreationForm

from user.models import User


class SignupForm(UserCreationForm):
    
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number', 'national_code', 'address')
