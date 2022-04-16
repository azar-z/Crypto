from django.contrib import messages
from django.shortcuts import redirect, render

from trade.forms.transfer_confirm import TransferConfirmForm


def transfer_request_view(request, pk):
    order = request.user.orders.get(pk=pk)
    account = order.get_first_step_account()
    currency = order.source_currency_type
    amount = order.first_step_id_in_account
    address = order.second_step_wallet_address
    response = account.request_withdraw(currency, amount, address)
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


def transfer_confirm_view(request, pk):
    order = request.user.orders.get(pk=pk)
    account = order.get_first_step_account()
    if request.method == 'POST':
        form = TransferConfirmForm(request.POST)
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
        form = TransferConfirmForm()
    return render(request, 'trade/transfer_confirm.html', {'form': form})


def transfer_cancel_view(request, pk):
    order = request.user.orders.get(pk=pk)
    messages.success(request, 'Transfer cancel was successful.')
    order.status = 'TOU'
    order.save()
    return redirect('message_view')
