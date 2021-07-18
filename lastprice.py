import pandas as pd
from datetime import time

pricefilepath = 'data_18m.csv'
pricesdf = pd.read_csv(pricefilepath, parse_dates=['time'])

pricesdf = pricesdf.drop_duplicates()

pricesdf.dropna(inplace=True)

pricesdf = pricesdf[pricesdf.time.dt.time >= time(7, 00, 00)]
pricesdf = pricesdf[pricesdf.time.dt.time <= time(14, 55, 00)]

pricesdf.time = pd.to_datetime(pricesdf.time)

daily_close_index = pricesdf.groupby(["symbol", pricesdf.time.dt.floor('d')])['time'].last(1)

daily_close_index = pd.Index(daily_close_index.droplevel(1).reset_index())

pricesdf = pricesdf.set_index(["symbol", "time"])

last_prices = pricesdf.loc[daily_close_index]

export_path = 'last_' + pricefilepath

last_price = last_prices.groupby(level=[0, 1]).last(1)

last_price.to_csv(export_path)

