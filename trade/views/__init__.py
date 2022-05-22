from .compare_prices import *
from .new_trade import *
from .profit_and_loss import *
from .alerts import *
from .transfer_request_and_confirm import *
from .order_list import *
from .order_detail import *
from .golden_trades import *
from .django_table_record import *
from .html_table_record import *
from .poll_for_download import *
from .get_autocomplete_data import *


def message_view(request):
    return render(request, 'user/message_template.html')
