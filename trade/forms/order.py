from django import forms
from django.core.exceptions import ValidationError

from trade.models import Order
from user.models.account import ACCOUNT_TYPE_CHOICES

SELL_OR_BUY = ((True, '  sell    '), (False, '    buy   '))


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
    no_second_step = forms.BooleanField(label='Doesn\'t have second action.', required=False)

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['account_type'].label = 'Source'
        second_step_fields = ['second_step_account_type', 'max_price', 'min_price']
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

    def clean_max_price(self):
        max_price = self.cleaned_data['max_price']
        if max_price is None:
            return max_price
        price = self.cleaned_data['price']
        if max_price <= price:
            raise ValidationError('Maximum price should be greater than price')
        return max_price

    def clean_min_price(self):
        min_price = self.cleaned_data['min_price']
        if min_price is None:
            return min_price
        price = self.cleaned_data['price']
        if min_price >= price:
            raise ValidationError('Minimum price should be less than price')
        return min_price

    def clean_source_currency_amount(self):
        source_currency_amount = self.cleaned_data['source_currency_amount']
        if not source_currency_amount:
            raise ValidationError('Amount is too small')
        return source_currency_amount

    class Meta:
        model = Order
        fields = ['source_currency_type', 'is_sell', 'account_type', 'source_currency_amount', 'price',
                  'no_second_step', 'second_step_account_type',
                  'max_price', 'min_price']
