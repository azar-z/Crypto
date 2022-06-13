from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user.tasks.send_email import send_email_task
from user.tokens import account_activation_token


def signup_logic(current_site, form):
    user = form.save(commit=False)
    user.is_active = False
    user.save()
    context = {
                                'user': user,
                                'domain': current_site.domain,
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'token': account_activation_token.make_token(user),
                            }
    msg_html = render_to_string('user/emails/activation.html', context)
    send_email_task.delay('Activate your crypto account.', msg_html, [user.email])
