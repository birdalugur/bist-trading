#!/usr/bin/env python
# coding: utf-8

import multiprocessing
import pandas as pd

import mydata
from trading_table import trading_table

folder_path = 'data/'

all_paths = mydata.get_file_paths(folder_path)

data = mydata.read_multiple_data(all_paths)

data = data[data.symbol.isin(mydata.BIST30)]

data = data.set_index('time')

data['mid_price'] = data['bid_price'] + data['ask_price']

mid_price = data.pivot_table(index='time', columns='symbol', values='mid_price', aggfunc='mean')
bid_price = data.pivot_table(index='time', columns='symbol', values='bid_price', aggfunc='last')
ask_price = data.pivot_table(index='time', columns='symbol', values='ask_price', aggfunc='last')

del (data, folder_path, all_paths)

time_range = mydata.time_range(ask_price, bid_price)

mid_index = mid_price.index.append(time_range).drop_duplicates().sort_values()
bid_index = bid_price.index.append(time_range).drop_duplicates().sort_values()
ask_index = ask_price.index.append(time_range).drop_duplicates().sort_values()

mid_price = mid_price.reindex(mid_index)
bid_price = bid_price.reindex(bid_index)
ask_price = ask_price.reindex(ask_index)

ask_price = ask_price.resample('D').apply(lambda x: x.apply(lambda x: x[:x.last_valid_index()].ffill())).droplevel(0)
bid_price = bid_price.resample('D').apply(lambda x: x.apply(lambda x: x[:x.last_valid_index()].ffill())).droplevel(0)

mid_price = mid_price.groupby(pd.Grouper(freq='D')).resample('5Min').mean().droplevel(0)

mid_price = mid_price.resample('D').apply(lambda x: x.apply(lambda x: x[:x.last_valid_index()].ffill())).droplevel(0)

del (ask_index, bid_index, mid_index, time_range)

# parameters

pair_names = mydata.pair_names
data_freq = '5Min'
window_size = 300
threshold = 1
intercept = False
wavelet = False

all_stats = []
all_buy_sell = []


def run(pair_name):
    print(pair_name)
    pair_mid = mid_price.loc[:, pair_name]
    pair_ask = ask_price.loc[:, pair_name]
    pair_bid = bid_price.loc[:, pair_name]
    pair_mid.dropna(inplace=True)
    pair_ask.dropna(inplace=True)
    pair_bid.dropna(inplace=True)
    trade_table = trading_table(pair_mid, pair_ask, pair_bid, window_size, pair_name, threshold, intercept, wavelet)

    return trade_table


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=8)
    results = pool.map(run, pair_names)

    df_trade_table = pd.concat(results)

    file_name = 'roll_' + str(window_size) + \
                '_freq_' + data_freq + \
                '_thr_' + str(threshold) + \
                '_int_' + str(intercept) + \
                '_wavelets_' + str(wavelet)

    df_trade_table.to_csv(file_name + '_tradeTable' + '.csv')
