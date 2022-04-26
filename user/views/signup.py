import requests
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from user.forms.signup import SignupForm
from user.logics.signup import signup_logic
from user.models import User
from user.tokens import account_activation_token


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            current_site = get_current_site(request)
            signup_logic(current_site, form)
            messages.info(request, 'Please confirm your email address to complete the registration')
            return render(request, 'user/message_template.html')
    else:
        form = SignupForm()
    return render(request, 'user/signup.html', {'form': form})


def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Email confirmation was successful. Welcome to crypto.')
    else:
        messages.error(request, 'Activation link is invalid!')
    return redirect('home')


def test(request):
    headers = {
        'Authorization': 'Token ' + request.user.nobitex_account.token
    }
    response = requests.post('https://api.nobitex.ir/users/wallets/list', headers=headers)
    response = response.json()
    return HttpResponse(response['wallets'][0]['depositAddress'])
