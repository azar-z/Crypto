from celery import shared_task

from data.tasks.add_columns import add_indicator_columns, add_all_columns
from data.tasks.bi_dashboard_plots import make_plots
from data.tasks.btc_price_prediction import predict_bitcoin_price
from data.tasks.create_price_file import unify_all_price_files, download_data_from_binance
from data.tasks.user_profit_prediction import make_predictor_model
from user.models import User


@shared_task
def user_data_task():
    User.export_data()
    make_plots()
    make_predictor_model()


@shared_task
def price_data_task():
    download_data_from_binance()
    unify_all_price_files()
    add_all_columns()
    predict_bitcoin_price()
