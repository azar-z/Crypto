import pandas as pd
from django.core.cache import cache
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import QuantileTransformer


def shift_row_up(column, df):
    df[column] = df[column].shift(-1)
    return df


def predict_bitcoin_price():
    df = pd.read_csv('price_data/all_prices_with_indicator.csv')
    df = df.drop(['Open time', 'Close time'], axis=1)
    last_row = df.iloc[-1]
    predicted_params = ['Open', 'High', 'Low', 'Close', 'Number of trades']
    for item in predicted_params:
        df = shift_row_up(item, df)
    df.drop(df.tail(1).index, inplace=True)
    x = df.drop(predicted_params, axis=1)
    last_row = last_row.drop(predicted_params)
    y = df[predicted_params]
    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=1, test_size=0.2)
    sc = QuantileTransformer()
    scaler = sc.fit(x_train)
    x_train_scaled = scaler.transform(x_train)
    regressor = MLPRegressor(random_state=1, max_iter=1500, activation='relu',
                             solver='adam'
                             ).fit(x_train_scaled, y_train)
    last_row_dataframe = pd.DataFrame([last_row.tolist()], columns=last_row.index)
    last_row_dataframe_scaled = scaler.transform(last_row_dataframe)
    prediction = regressor.predict(last_row_dataframe_scaled)
    prediction_series = pd.Series(prediction[0], index=predicted_params)
    cache_key = 'BTC_price_prediction'
    cache.set(cache_key, prediction_series)

    # # # # # # # # # # # # # # # # # # test: # # # # # # # # # # # # # # # # # # #
    # x_test_scaled = scaler.transform(x_test)
    # prediction = regressor.predict(x_test_scaled)
    # score = regressor.score(x_test_scaled, y_test)
    # print(prediction)
    # print(y_test)
    # print(score)
