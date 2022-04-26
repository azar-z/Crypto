from django import forms
from django.core.exceptions import ValidationError

from trade.models import Order
from user.models.account import ACCOUNT_TYPE_CHOICES

SELL_OR_BUY = ((True, '  sell    '), (False, '    buy   '))


def clean_limit(is_greater, is_lower, name):
    if is_greater:
        raise ValidationError(name + ' limit should be less than price.')
    if is_lower:
        raise ValidationError(name + ' limit should be greater than price.')
    return


class OrderForm(forms.ModelForm):
    is_sell = forms.TypedChoiceField(
        label='',
        coerce=lambda x: x == 'True',
        choices=SELL_OR_BUY,
        widget=forms.RadioSelect,
        required=True
    )
    second_step_account_type = forms.ChoiceField(widget=forms.Select, choices=ACCOUNT_TYPE_CHOICES, required=False,
                                                 label='Destination')
    no_second_step = forms.BooleanField(label='Doesn\'t have any limits.', required=False)

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['account_type'].label = 'Source'
        second_step_fields = ['second_step_account_type', 'profit_limit', 'loss_limit']
        for field in second_step_fields:
            self.fields[field].widget.attrs.update({'class': 'second_step_field'})

    def save(self, commit=True):
        order = super(OrderForm, self).save(commit=False)
        has_second_step = not self.cleaned_data['no_second_step']
        if has_second_step:
            second_step_account_type = self.cleaned_data['second_step_account_type']
            if second_step_account_type is None:
                second_step_account_type = self.cleaned_data['account_type']
            source_currency_type = self.cleaned_data['source_currency_type']
            second_step_is_sell = not self.cleaned_data['is_sell']
            second_step = Order.objects.create(account_type=second_step_account_type, is_sell=second_step_is_sell
                                           , source_currency_type=source_currency_type)
            order.next_step = second_step
        if commit:
            order.save()
        return order

    def clean_profit_limit(self):
        profit_limit = self.cleaned_data['profit_limit']
        if profit_limit is None:
            return profit_limit
        price = self.cleaned_data['price']
        is_sell = self.cleaned_data['is_sell']
        clean_limit(is_sell and profit_limit >= price, not is_sell and profit_limit <= price, 'Profit')
        return profit_limit

    def clean_loss_limit(self):
        loss_limit = self.cleaned_data['loss_limit']
        if loss_limit is None:
            return loss_limit
        price = self.cleaned_data['price']
        is_sell = self.cleaned_data['is_sell']
        clean_limit(not is_sell and loss_limit >= price, is_sell and loss_limit <= price, 'Loss')
        return loss_limit

    class Meta:
        model = Order
        fields = ['source_currency_type', 'is_sell', 'account_type', 'source_currency_amount', 'price',
                  'no_second_step', 'second_step_account_type',
                  'profit_limit', 'loss_limit']




