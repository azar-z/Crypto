import pandas as pd
from ta import add_all_ta_features

from data.tasks.gather_extra_price_data import google_trends_data_collector, get_finance_data


def add_indicator_columns():
    df = pd.read_csv('price_data/all_prices.csv', parse_dates=True)
    df = add_all_ta_features(
        df, open="Open", high="High", low="Low", close="Close", volume="Number of trades", fillna=True)
    df.dropna()
    df.to_csv('price_data/all_prices_with_indicator.csv', index=False)


def add_all_columns():
    list_of_stocks = ['GOLD', 'OIL', 'SNP', 'NDX', 'DX-Y.NYB']
    for stock in list_of_stocks:
        get_finance_data(stock)
        add_column(stock)
    google_trends_data_collector()
    add_column('google_trends')
    add_indicator_columns()


def add_column(column_name):
    df = pd.read_csv('price_data/all_prices.csv', parse_dates=True)
    column_dataframe = pd.read_csv('price_data/extra_data/' + column_name + '.csv')
    column_dataframe = column_dataframe.loc[column_dataframe.index.repeat(4)].reset_index(drop=True)
    df[column_name] = column_dataframe[column_name]
    df.to_csv('price_data/all_prices.csv', index=False)
