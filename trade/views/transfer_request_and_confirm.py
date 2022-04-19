from django.contrib import messages
from django.shortcuts import redirect, render

from trade.forms.otp import OTPForm
from trade.forms.wallet_address import WalletAddressForm
from user.errors import NoAuthenticationInformation


def transfer_request_view(request, pk):
    order = request.user.orders.get(pk=pk)
    if request.method == 'POST':
        form = WalletAddressForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data.get('deposit_wallet_address')
            order.deposit_wallet_address = address
            order.save()
            account = order.get_account()
            try:
                response = order.request_withdraw()
            except NoAuthenticationInformation:
                messages.error(request,
                               'We need your authentication information for transferring currencies from this account')
                return redirect('accounts', account_type=order.account_type)
            need_confirmation = account.needs_withdraw_confirmation
            if response:
                messages.success(request, 'Transfer request was successful.')
                if not need_confirmation:
                    order.status = 'TOS'
                else:
                    order.withdraw_id = str(response)
                    order.save()
                    return redirect('transfer_confirm', kwargs={'pk': order.pk})
            else:
                messages.error(request, 'Transfer request was not successful.')
                order.status = 'TOU'
            order.save()
            return redirect('message_view')
    else:
        form = WalletAddressForm()
    context = {
        'form': form,
        'currency': order.get_source_currency_type_display(),
        'account': order.next_step.get_account_type_display()
    }
    return render(request, 'trade/transfer_request.html', context=context)


def transfer_confirm_view(request, pk):
    order = request.user.orders.get(pk=pk)
    account = order.get_account()
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data.get('otp')
            withdraw_id = order.withdraw_id
            response = account.confirm_withdraw(withdraw_id, otp)
            if response:
                messages.success(request, 'Transfer confirm was successful.')
                order.status = 'TOS'
            else:
                messages.error(request, 'Transfer confirm was not successful.')
                order.status = 'TOU'
            order.save()
            return redirect('message_view')
    else:
        form = OTPForm()
    return render(request, 'trade/transfer_confirm.html', {'form': form})


def transfer_cancel_view(request, pk):
    order = request.user.orders.get(pk=pk)
    messages.success(request, 'Transfer cancel was successful.')
    order.status = 'TOU'
    order.save()
    return redirect('message_view')
