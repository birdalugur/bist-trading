import multiprocessing
from functools import partial
import pandas as pd

import mydata
from trading_table import trading_table

folder_path = 'data.csv'

mid_freq = '5Min'

data = pd.read_csv(folder_path, parse_dates=['time'])
print('reading: ok!')


data['mid_price'] = (data['bid_price'] + data['ask_price']) / 2

mid_price = data.pivot_table(index='time', columns='symbol', values='mid_price', aggfunc='mean')
bid_price = data.pivot_table(index='time', columns='symbol', values='bid_price', aggfunc='last')
ask_price = data.pivot_table(index='time', columns='symbol', values='ask_price', aggfunc='last')
print('pivot: ok!')
del (data, folder_path)

time_range = mydata.time_range(ask_price, bid_price)

mid_index = mid_price.index.append(time_range).drop_duplicates().sort_values()
bid_index = bid_price.index.append(time_range).drop_duplicates().sort_values()
ask_index = ask_price.index.append(time_range).drop_duplicates().sort_values()

mid_price = mid_price.reindex(mid_index)
bid_price = bid_price.reindex(bid_index)
ask_price = ask_price.reindex(ask_index)
print('reindex: ok!')
del (ask_index, bid_index, mid_index, time_range)


def fill_nan(x):
    x = x[:x.last_valid_index()]
    x = x.ffill()
    return x


mid_price = mid_price.groupby(pd.Grouper(freq='D')).resample(mid_freq).mean().droplevel(0)
mid_price = mid_price.resample('D').apply(fill_nan).droplevel(0)

ask_price = ask_price.resample('D').apply(fill_nan).droplevel(0)
bid_price = bid_price.resample('D').apply(fill_nan).droplevel(0)

mid_price.dropna(inplace=True)
ask_price.dropna(inplace=True)
bid_price.dropna(inplace=True)

mid_price.to_csv('mid_price.csv')
ask_price.to_csv('ask_price.csv')
bid_price.to_csv('bid_price.csv')
