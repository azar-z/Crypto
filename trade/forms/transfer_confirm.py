from django import forms


class TransferConfirmForm(forms.Form):
    otp = forms.CharField(label='OTP', max_length=100)
