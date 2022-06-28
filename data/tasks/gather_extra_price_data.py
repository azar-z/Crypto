import csv
import datetime

import pandas as pd
import yfinance as yf

from django.utils import timezone
from pytrends.request import TrendReq


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

    previous_date = datetime.datetime(year=2022, month=1, day=1) + datetime.timedelta(days=-1)
    for index, row in df.iterrows():
        current_date = pd.to_datetime(index)
        if current_date.year != 2022:
            # 2021 days
            df = df.drop(index)
        else:
            # for days that were not recorded:
            delta_date = (current_date - previous_date).days
            while delta_date > 1:
                new_date = (previous_date + datetime.timedelta(days=delta_date - 1))
                df.loc[new_date] = [row[name]]
                delta_date -= 1
        previous_date = current_date
    df = df.sort_index()
    file_address = 'price_data/extra_data/' + name + '.csv'
    df.to_csv(file_address)
