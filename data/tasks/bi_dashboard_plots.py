import json

import mpld3
import pandas as pd
from django.core.cache import cache
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans

from trade.models import Order


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
    user_df = user_df.loc[:, df.columns.intersection(['city', 'total_transaction_b'])]
    data = user_df.to_numpy().tolist()
    data = [['city', 'total_transaction_b']] + data
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
    df = df[['total_transaction_b', 'total_profit_or_loss_b']].copy()
    kmeans = KMeans(n_clusters=3).fit(df)
    centroids = kmeans.cluster_centers_
    plots = plt.scatter(df['total_transaction_b'], df['total_profit_or_loss_b'], c=kmeans.labels_.astype(float), s=50, alpha=0.5)
    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', s=50)
    plt.xlabel("total transaction (billion USDT)")
    plt.ylabel("total profit (billion USDT)")
    figure = plots.figure
    mpld3.plugins.connect(figure)
    plot_in_html = mpld3.fig_to_html(figure)
    return plot_in_html
