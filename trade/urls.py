"""crypto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path

    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from trade import views

urlpatterns = [

    # trading tools
    path('new/', views.NewTradeView.as_view(), name='new_trade'),
    path('prices/compare/', views.ComparePricesView.as_view(), name='compare_prices'),
    path('orderbook-and-trades/', views.get_orderbook_and_trades_view, name='get_orderbook_and_trades'),
    path('profit_and_loss/', views.ProfitAndLossView.as_view(), name='profit_and_loss'),
    path('transfer/alerts/', views.TransferAlertsView.as_view(), name='transfer_alerts'),
    path('transfer/request/<int:pk>/', views.transfer_request_view, name='transfer_request'),
    path('transfer/confirm/<int:pk>/', views.transfer_confirm_view, name='transfer_confirm'),
    path('transfer/cancel/<int:pk>/', views.transfer_cancel_view, name='transfer_cancel'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('home/', views.GoldenTrades.as_view(), name='home'),

    # record
    path('record/django_table/', views.DjangoTableOrderRecordView.as_view(), name='django_table_record'),
    path('record/html/', views.HTMLOrderRecordView.as_view(), name='html_record'),
    path('poll_for_download/', views.poll_for_download, name='poll_for_download'),
    path('get_usernames/', views.get_usernames, name='get_usernames'),
    path('get_emails/', views.get_emails, name='get_emails'),

    path('message/', views.message_view, name='message_view'),

]
