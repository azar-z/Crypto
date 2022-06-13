import environ

from trade.fake_data_utils import create_two_step_order, create_one_step_order
from user.fake_data_utils import create_fake_user


env = environ.Env()
environ.Env.read_env()
NOBITEX_TOKEN = env('NOBITEX_TOKEN')
NOBITEX_DONE_ORDER_ID = env('NOBITEX_DONE_ORDER_ID')


def create_user():
    return create_fake_user()


def create_order(owner=None, is_two_step=False):
    if is_two_step:
        order = create_two_step_order(owner)
    else:
        order = create_one_step_order(owner)
    return order


def make_order_impossible(order):
    order.source_currency_type = 'BTC'
    order.amount = '1'
    order.save()


def make_user_authenticated_in_account(user, account_type='N'):
    if account_type == 'N':
        user.nobitex_account.token = NOBITEX_TOKEN
        user.nobitex_account.save()


def make_order_authenticated(order, account_type='N'):
    order.account_type = account_type
    order.save()
    make_user_authenticated_in_account(order.owner, account_type)


def set_limits_for_two_step_order(order, is_sell, price=187.99,
                                  min_price=98.00,
                                  max_price=243.77):
    order.status = 'OD'
    order.is_sell = is_sell
    order.price = price
    order.next_step.is_sell = not is_sell
    order.min_price = min_price
    order.max_price = max_price
    order.save()


def create_n_step_order(n, owner=None):
    first_order = create_order(owner)
    order = first_order
    for _ in range(n - 1):
        order.next_step = create_order(owner)
        order.save()
        order = order.next_step
    return first_order

