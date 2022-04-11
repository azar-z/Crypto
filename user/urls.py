"""crypto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path

    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import django.contrib.auth.views as auth_views
from django.urls import path, re_path
from django.views.generic import TemplateView

from user import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('signup/', views.signup_view, name='signup'),


    path('user_panel', TemplateView.as_view(template_name='user/profile/user_panel.html'), name='user_panel'),
    path('change_username/<int:pk>', views.ChangeUsernameView.as_view(), name='change_username'),
    path('change_email/<int:pk>', views.ChangeEmailView.as_view(), name='change_email'),
    path('change_phone_number/<int:pk>', views.ChangePhoneNumberView.as_view(), name='change_phone_number'),
    path('change_address/<int:pk>', views.ChangeAddressView.as_view(), name='change_address'),
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='user/profile/password_change.html'), name='password_change'),
    path('change_password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='user/profile/password_change_done.html'), name='password_change_done'),

    path('accounts/<slug:account_type>/', views.accounts_view, name='accounts'),

    path('trades/new/', views.NewTradeView.as_view(), name='new_trade'),

    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,100})/$',
            views.activate_view, name='activate'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='user/password_reset/password_reset_form.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset/password_reset_complete.html'), name='password_reset_complete'),


    path('test/', views.test)
]
