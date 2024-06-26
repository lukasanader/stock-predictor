import math
import numpy as np
import pandas_datareader as web
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense,LSTM
import matplotlib.pyplot as plt
import quandl
import yfinance as yf

# Fetch data
df = yf.download("MSFT", start="2015-01-01", end="2024-04-17")
plt.style.use('fivethirtyeight')
#df = web.DataReader('AAPL', data_source='yahoo', start='2012-01-01', end='2019-12-17')
data = df.filter(['Close'])
dataset = data.values

training_data_len = math.ceil(len(dataset)*.8)

scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)

train_data = scaled_data[0:training_data_len, :]

x_train = []
y_train = []
for i in range(60, len(train_data)):
    x_train.append(train_data[i-60:i,0])
    y_train.append(train_data[i, 0])
    if i<= 60:
        print(x_train)
        print(y_train)
        print() 
x_train, y_train = np.array(x_train), np.array(y_train)

x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

model = Sequential()
model.add(LSTM(75, return_sequences=True,input_shape=(x_train.shape[1], 1)))
model.add(LSTM(75, return_sequences=False))
model.add(Dense(35))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')

#train
model.fit(x_train,y_train, batch_size=1, epochs=1)

test_data = scaled_data[training_data_len - 60: , :]
x_test = []
y_test = dataset[training_data_len:, :]
for i in range(60, len(test_data)):
    x_test.append(test_data[i-60:i,0])

x_test = np.array(x_test)

x_test = np.reshape(x_test, (x_test.shape[0],x_test.shape[1], 1))

predicitions = model.predict(x_test)
predicitions = scaler.inverse_transform(predicitions)

rmse = np.sqrt( np.mean(predicitions - y_test)**2)
train = data[:training_data_len]
valid = data[training_data_len:]
valid['Predictions'] = predicitions
plt.figure(figsize=(16,8))
plt.title('Model')
plt.xlabel('Date',fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.plot(train['Close'])
plt.plot(valid[['Close', 'Predictions']])
plt.legend(['Train', 'Val', 'Predictions'], loc = 'lower right')
plt.show()
