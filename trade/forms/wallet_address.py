from django import forms


class WalletAddressForm(forms.Form):
    deposit_wallet_address = forms.CharField(max_length=100)
