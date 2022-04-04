from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from user.models import User
from user.tokens import account_activation_token


def signup_logic(request, form):
    user = form.save(commit=False)
    user.is_active = False
    user.save()
    current_site = get_current_site(request)
    user.send_email_to_user('Activate your crypto account.',
                            'user/emails/activation.html',
                            {
                                'user': user,
                                'domain': current_site.domain,
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'token': account_activation_token.make_token(user),
                            }
                            )
    messages.info(request, 'Please confirm your email address to complete the registration')


def activate_logic(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Email confirmation was successful. Now you can login to your account.')
    else:
        messages.error(request, 'Activation link is invalid!')
