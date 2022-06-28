import pandas as pd
from django.core.cache import cache
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler


def make_predictor_model():
    df = pd.read_csv('exported_data/user_data.csv')
    df = df.drop(['id', 'username', 'phone_number', 'national_code', 'address',
                  'birthday', 'total_profit_or_loss', 'city', 'total_transaction_b', 'total_profit_or_loss_b'], axis=1)
    x = df.drop('total_profit_or_loss_percent', axis=1)
    y = df['total_profit_or_loss_percent']
    x_train, x_test, y_train, y_test = train_test_split(x, y,
                                                        random_state=1, test_size=0.2)
    sc = MinMaxScaler()
    scaler = sc.fit(x_train)
    x_train_scaled = scaler.transform(x_train)
    regressor = MLPRegressor(random_state=1,
                             max_iter=500, activation='relu',
                             solver='adam'
                             ).fit(x_train_scaled, y_train)
    cache_key = 'regressor'
    cache.set(cache_key, regressor)
    cache_key = 'scaler'
    cache.set(cache_key, scaler)
    # # # # # # # # # # # # # # # # # # test: # # # # # # # # # # # # # # # # # # #
    # x_test_scaled = scaler.transform(x_test)
    # prediction = regressor.predict(x_test_scaled)
    # comparison = pd.DataFrame({'Actual': y_test, 'Predicted': prediction})
    # score = regressor.score(x_test_scaled, y_test)
    # print(comparison)
    # print(score)
