import csv
import datetime
import glob
import os
import zipfile

import requests


def unify_all_price_files():
    files = glob.glob("price_data/2022/*.csv")
    files.sort()
    fout = open("price_data/all_prices.csv", "w")
    head = ['Open time', 'Open', 'High', 'Low', 'Close', 'Close time', 'Number of trades']
    writer = csv.writer(fout)
    writer.writerow(head)
    for file in files:
        f = open(file)
        reader = csv.reader(f)
        writer = csv.writer(fout)
        for r in reader:
            writer.writerow((r[0], r[1], r[2], r[3], r[4], r[6], r[8]))
        f.close()
    fout.close()


def download_data_from_binance():
    changed = False
    date = datetime.date.today() + datetime.timedelta(days=-1)
    path_to_zip_file = date.strftime('price_data_zip_files/20%y/BTCUSDT-6h-20%y-%m-%d.zip')
    while not os.path.exists(path_to_zip_file) and date.year == 2022:
        url = date.strftime(
            'https://data.binance.vision/data/futures/um/daily/markPriceKlines/BTCUSDT/6h/BTCUSDT-6h-20%y-%m-%d.zip')
        response = requests.get(url)
        if response.status_code != 404:
            open(path_to_zip_file, "wb").write(response.content)
            with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
                zip_ref.extractall('price_data/{year}/'.format(year=date.year))
            changed = True
        date = date + datetime.timedelta(days=-1)
        path_to_zip_file = date.strftime('price_data_zip_files/20%y/BTCUSDT-6h-20%y-%m-%d.zip')
