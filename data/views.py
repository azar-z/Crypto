import datetime
import os
import zipfile

import requests
from django.http import HttpResponse


def download(request):
    date = datetime.date(year=2021, month=1, day=19)
    while date.year == 2021:
        path_to_zip_file = date.strftime('price_data_zip_files/20%y/BTCUSDT-1m-20%y-%m-%d.zip')
        if not os.path.exists(path_to_zip_file):
            url = date.strftime('https://data.binance.vision/data/futures/um/daily/markPriceKlines/BTCUSDT/1m/BTCUSDT-1m-20%y-%m-%d.zip')
            response = requests.get(url)
            open(path_to_zip_file, "wb").write(response.content)
            try:
                with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
                    zip_ref.extractall('price_data/{year}/'.format(year=date.year))
            except zipfile.BadZipFile:
                pass
        date = date + datetime.timedelta(days=1)
    return HttpResponse('done')
