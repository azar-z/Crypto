from django.shortcuts import render, redirect

from user.forms.signup import SignupForm
from user.logics.signup import signup_logic, activate_logic


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            signup_logic(request, form)
            return render(request, 'user/message_template.html')
    else:
        form = SignupForm()
    return render(request, 'user/signup.html', {'form': form})


def activate_view(request, uidb64, token):
    activate_logic(request, uidb64, token)
    return redirect('user:home')
