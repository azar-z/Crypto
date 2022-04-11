from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from user.errors import NoAuthenticationInformation
from user.logics.accounts import get_account_form_based_on_type, get_account_based_on_type


@login_required()
def accounts_view(request, account_type):
    if request.method == 'POST':
        form = get_account_form_based_on_type(request.user, request.POST, account_type)
        if form.is_valid():
            form.save()
            return redirect('accounts', account_type=account_type)
    else:
        context = {'active_tab': account_type}
        account = get_account_based_on_type(request.user, account_type)
        form = get_account_form_based_on_type(request.user, None, account_type)
        context.update({
            'form': form,
        })
        try:
            context.update({
                'balances': account.get_balance_of_all_currencies(),
            })
        except NoAuthenticationInformation:
            context.update({'error': 'Please update the account information so we can connect to your account.'})
        return render(request, 'user/accounts/account_detail.html', context)
