from user.forms.update_account_info import WallexAuthentication, NobitexAuthentication, ExirAuthentication


def get_account_form_based_on_type(user, data, account_type):
    if account_type == 'N':
        return NobitexAuthentication(data, instance=user.nobitex_account)
    if account_type == 'W':
        return WallexAuthentication(data, instance=user.wallex_account)
    if account_type == 'E':
        return ExirAuthentication(data, instance=user.exir_account)


def get_account_based_on_type(user, account_type):
    if account_type == 'N':
        return user.nobitex_account
    if account_type == 'W':
        return user.wallex_account
    if account_type == 'E':
        return user.exir_account
