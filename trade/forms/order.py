from django import forms
from django.core.exceptions import ValidationError

from trade.models import Order

YES_NO = ((True, '  Yes,Want to sell it    '), (False, '    No,Want to buy it    '))


class OrderForm(forms.ModelForm):
    is_sell = forms.TypedChoiceField(
        label='Want to sell the first currency?',
        coerce=lambda x: x == 'True',
        choices=YES_NO,
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        second_step_fields = ['second_step_account_type', 'profit_limit', 'loss_limit', 'second_step_wallet_address']
        for field in second_step_fields:
            self.fields[field].widget.attrs.update({'class': 'second_step_field'})

    def save(self, commit=True):
        order = super(OrderForm, self).save(commit=False)
        if order.second_step_account_type is None:
            order.second_step_account_type = order.first_step_account_type
        if commit:
            order.save()
        return order

    def clean_has_second_step(self):
        has_second_step = self.cleaned_data['has_second_step']
        is_sell = self.cleaned_data['is_sell']
        if has_second_step and is_sell:
            raise ValidationError("You can only sell the first currency afterwards if you buy it.")
        return has_second_step

    class Meta:
        model = Order
        fields = ['first_step_account_type', 'source_currency_type', 'dest_currency_type',
                  'source_currency_amount', 'price', 'is_sell', 'has_second_step', 'second_step_account_type',
                  'profit_limit', 'loss_limit', 'second_step_wallet_address']
        help_texts = {
            'second_step_wallet_address': 'Leave this blank if first step and second step accounts are the same.',
            'second_step_account_type': 'If you leave this blank, the first step account type would be chosen.',
        }

