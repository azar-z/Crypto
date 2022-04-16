from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from trade.models import Order


@method_decorator(login_required, name='dispatch')
class OrderDetailView(DetailView):
    template_name = 'trade/order_detail.html'
    model = Order
    context_object_name = 'order'

    def get_queryset(self):
        return self.request.user.orders.all()


