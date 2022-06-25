import pandas as pd
from django import forms
from django.core.cache import cache

MAN_OR_WOMAN = ((True, '  Woman    '), (False, '    Man   '))


class PredictionForm(forms.Form):
    age = forms.IntegerField(max_value=120, min_value=18)
    is_woman = forms.TypedChoiceField(
        label='',
        coerce=lambda x: x == 'True',
        choices=MAN_OR_WOMAN,
        widget=forms.RadioSelect,
        required=True
    )
    total_transaction = forms.FloatField()

    def predict_profit_percent(self):
        age = self.cleaned_data.get('age')
        is_woman = self.cleaned_data.get('is_woman')
        total_transaction = self.cleaned_data.get('total_transaction')
        user_dict = {
            'age': [age],
            'is_woman': [is_woman],
            'total_transaction': [total_transaction],
        }
        df = pd.DataFrame(user_dict)
        x_test = df
        cache_key = 'regressor'
        regressor = cache.get(cache_key)
        cache_key = 'scaler'
        scaler = cache.get(cache_key)
        x_test_scaled = scaler.transform(x_test)
        prediction = regressor.predict(x_test_scaled)
        return prediction[0]
