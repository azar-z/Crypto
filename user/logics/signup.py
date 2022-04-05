from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from user.models import User
from user.tokens import account_activation_token


def signup_logic(current_site, form):
    user = form.save(commit=False)
    user.is_active = False
    user.save()
    user.send_email_to_user('Activate your crypto account.',
                            'user/emails/activation.html',
                            {
                                'user': user,
                                'domain': current_site.domain,
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'token': account_activation_token.make_token(user),
                            }
                            )
