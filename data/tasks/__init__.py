import csv
import datetime
import glob
import json
import os.path
import zipfile

import mpld3
import pandas as pd
import requests
import yfinance as yf
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from matplotlib import pyplot as plt
from pytrends.request import TrendReq
from sklearn.cluster import KMeans
from ta import add_all_ta_features

from data.tasks.user_profit_prediction import make_predictor_model
from trade.models import Order
from user.models import User


@shared_task
def export_user_data_task():
    User.export_data()
    make_plots()
    make_predictor_model()


@shared_task
def add_indicator_columns():
    df = pd.read_csv('price_data/all_prices.csv', parse_dates=True)
    df = add_all_ta_features(
        df, open="Open", high="High", low="Low", close="Close", volume="Number of trades", fillna=True)
    df.dropna()
    df.to_csv('price_data/all_prices_with_indicator.csv', index=False)


@shared_task
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
    add_all_columns()


def add_all_columns():
    list_of_stocks = ['GOLD', 'OIL', 'SNP', 'NDX', 'DX-Y.NYB']
    for stock in list_of_stocks:
        get_finance_data(stock)
        add_column(stock)
    google_trends_data_collector()
    add_column('google_trends')
    add_indicator_columns()


@shared_task
def add_column(column_name):
    df = pd.read_csv('price_data/all_prices.csv', parse_dates=True)
    column_dataframe = pd.read_csv('price_data/extra_data/' + column_name + '.csv')
    column_dataframe = column_dataframe.loc[column_dataframe.index.repeat(4)].reset_index(drop=True)
    df[column_name] = column_dataframe[column_name]
    df.to_csv('price_data/all_prices.csv', index=False)


@shared_task
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
    unify_all_price_files()


def make_plots():
    context = {}
    df = pd.read_csv('exported_data/user_data.csv')
    df['count'] = 1

    # sexuality
    df.insert(0, 'sexuality', 'Man')
    df.loc[df['is_woman'], ['sexuality']] = 'Woman'
    user_df = df.groupby(['sexuality']).count()
    user_df = user_df.loc[:, df.columns.intersection(['count'])]
    user_df.insert(0, 'sexuality', list(user_df.index.values))
    data = user_df.to_numpy().tolist()
    data = [['sexuality', 'num_of_users']] + data
    context.update({'sexuality': json.dumps(data)})

    # city
    user_df = df.groupby(['city']).count()
    user_df.insert(0, 'city', list(user_df.index.values))
    user_df = user_df.loc[:, df.columns.intersection(['city', 'count'])]
    data = user_df.to_numpy().tolist()
    data = [['city', 'num_of_users']] + data
    context.update({'city': json.dumps(data)})

    # city profit
    user_df = df.groupby(['city']).sum()
    user_df.insert(0, 'city', list(user_df.index.values))
    user_df = user_df.loc[:, df.columns.intersection(['city', 'total_transaction'])]
    data = user_df.to_numpy().tolist()
    data = [['city', 'total_transaction']] + data
    context.update({'city_profit': json.dumps(data)})

    # popular coin
    df = pd.DataFrame(list(Order.objects.all().values('source_currency_type')))
    df['count'] = 1
    order_df = df.groupby(['source_currency_type']).count()
    order_df.insert(0, 'source_currency_type', list(order_df.index.values))
    data = order_df.to_numpy().tolist()
    data = [['Coin', 'popularity']] + data
    context.update({'coins_popularity': json.dumps(data)})

    # user clustering
    context.update({'user_clustering': cluster_users_based_on_transaction_volume()})

    value = context
    cache_key = 'bi_dashboard_data'
    cache.set(cache_key, value)


def cluster_users_based_on_transaction_volume():
    df = pd.read_csv('exported_data/user_data.csv')
    df = df[['total_transaction', 'total_profit_or_loss']].copy()
    kmeans = KMeans(n_clusters=3).fit(df)
    centroids = kmeans.cluster_centers_
    plots = plt.scatter(df['total_transaction'], df['total_profit_or_loss'], c=kmeans.labels_.astype(float), s=50, alpha=0.5)
    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', s=50)
    plt.xlabel("total transaction (billion USDT)")
    plt.ylabel("total profit (billion USDT)")
    figure = plots.figure
    mpld3.plugins.connect(figure)
    plot_in_html = mpld3.fig_to_html(figure)
    return plot_in_html


def google_trends_data_collector():
    pytrends = TrendReq(hl='en-US', tz=360)
    time_now = timezone.now()
    word = 'bitcoin'
    trends = pytrends.get_historical_interest([word],
                                              year_start=time_now.year, month_start=time_now.month,
                                              day_start=time_now.day, hour_start=0,
                                              year_end=time_now.year, month_end=time_now.month, day_end=time_now.day,
                                              hour_end=0,
                                              cat=0, geo='', gprop='', sleep=60)
    word_trend = trends.iloc[0][word]
    new_row = [time_now.strftime('20%y-%m-%d'), word_trend]
    file_name = 'price_data/extra_data/google_trends.csv'
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow(new_row)


def get_finance_data(name):
    stock = yf.Ticker(name)
    df = stock.history(period="1y")
    df = df['High'].to_frame()
    df.columns = [name]
    for index in df.index.values:
        if pd.to_datetime(index).year != 2022:
            df = df.drop(index)
    file_address = 'price_data/extra_data/' + name + '.csv'
    df.to_csv(file_address)
