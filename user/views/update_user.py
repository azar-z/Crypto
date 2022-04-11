from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic

from user.models import User


@method_decorator(login_required, name='dispatch')
class ChangeUserInformationView(generic.UpdateView):
    model = User
    template_name = 'user/profile/update_user_information.html'
    fields = ['__all__']

    additional_context = {
        'title': 'Change Information'
    }

    def get_context_data(self, **kwargs):
        context = super(ChangeUserInformationView, self).get_context_data(**kwargs)
        context.update(self.additional_context)
        return context

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    class Meta:
        abstract = True


@method_decorator(login_required, 'dispatch')
class ChangeUsernameView(ChangeUserInformationView):
    fields = ['username']

    additional_context = {
        'title': 'Change Username'
    }


@method_decorator(login_required, 'dispatch')
class ChangeEmailView(ChangeUserInformationView):
    fields = ['email']

    additional_context = {
        'title': 'Change Email'
    }


@method_decorator(login_required, 'dispatch')
class ChangePhoneNumberView(ChangeUserInformationView):
    fields = ['phone_number']

    additional_context = {
        'title': 'Change Phone Number'
    }


@method_decorator(login_required, 'dispatch')
class ChangeAddressView(ChangeUserInformationView):
    fields = ['address']

    additional_context = {
        'title': 'Change Address'
    }
