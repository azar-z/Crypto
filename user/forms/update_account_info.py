from django import forms

from user.models import Nobitex, Wallex, Exir


class NobitexAuthentication(forms.ModelForm):
    class Meta:
        model = Nobitex
        fields = ['token']


class WallexAuthentication(forms.ModelForm):
    class Meta:
        model = Wallex
        fields = ['token']


class ExirAuthentication(forms.ModelForm):
    class Meta:
        model = Exir
        fields = ['api_key', 'api_signature', 'api_expires']
