import datetime

from celery import shared_task

from user.models import User
import requests
import zipfile
import os.path


@shared_task
def export_user_data_task():
    User.export_data()


@shared_task
def download_data_from_binance():
    date = datetime.date.today() + datetime.timedelta(days=-1)
    path_to_zip_file = date.strftime('price_data_zip_files/20%y/BTCUSDT-1m-20%y-%m-%d.zip')
    while not os.path.exists(path_to_zip_file):
        url = date.strftime('https://data.binance.vision/data/futures/um/daily/markPriceKlines/BTCUSDT/1m/BTCUSDT-1m-20%y-%m-%d.zip')
        response = requests.get(url)
        open(path_to_zip_file, "wb").write(response.content)
        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
            zip_ref.extractall('price_data/{year}/'.format(year=date.year))
        date = date + datetime.timedelta(days=-1)
        path_to_zip_file = date.strftime('price_data_zip_files/20%y/BTCUSDT-1m-20%y-%m-%d.zip')



