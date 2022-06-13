from django.core.cache import cache

from trade.models import Order
from user.models import User


def get_statistical_data():
    cache_key = 'statistical_data'
    if cache_key in cache:
        statistical_data = cache.get(cache_key)
    else:
        two_step_orders = Order.objects.exclude(owner=None).filter(previous_step=None). \
            exclude(next_step=None).exclude(next_step__price=0)
        total_profit = 0
        num_of_profitable = 0
        for order in two_step_orders:
            profit_or_loss = order.get_profit_or_loss()[0]
            if profit_or_loss > 0:
                total_profit += profit_or_loss
                num_of_profitable += 1
        statistical_data = {
            'user_number': User.objects.count(),
            'order_number': Order.objects.exclude(owner=None).count(),
            'number_of_profitable_orders': num_of_profitable,
            'total_profit_in_million': total_profit // 1000000,
        }
        cache.set(cache_key, statistical_data, timeout=600)
    return statistical_data
