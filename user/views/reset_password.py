from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.views import generic


class ResetPasswordView(generic.FormView):
    pass


class SendResetPasswordEmailView(generic.FormView):
    pass


