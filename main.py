#!/usr/bin/env python
# coding: utf-8

import multiprocessing
import pandas as pd
import mydata
import get_stats
from trading_table import trading_table


folder_path = '201911.csv'
use_cols = ['symbol', 'time', 'bid_price', 'ask_price']

data = pd.read_csv(folder_path, usecols=use_cols, converters={'time': lambda x: pd.Timestamp(int(x))})

data = data[data.symbol.isin(mydata.BIST30)]

bid_price = data.pivot_table(index='time', columns='symbol', values='bid_price')

ask_price = data.pivot_table(index='time', columns='symbol', values='ask_price')

mid_price = mydata.mid_price(data, agg_time='5Min')


ask_price = ask_price.resample('D').apply(lambda x: x.apply(lambda x: x[:x.last_valid_index()].ffill()))
bid_price = bid_price.resample('D').apply(lambda x: x.apply(lambda x: x[:x.last_valid_index()].ffill()))

ask_price = ask_price.droplevel(0)
bid_price = bid_price.droplevel(0)

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
    trade_table = trading_table(pair_mid, window_size, pair_name, threshold, intercept, wavelet)

    return trade_table


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=8)
    results = pool.map(run, pair_names)

    results = list(zip(*results))


    df_trade_table = pd.concat(results[2])

    file_name = 'roll_' + str(window_size) + \
                '_freq_' + data_freq + \
                '_thr_' + str(threshold) + \
                '_int_' + str(intercept) + \
                '_wavelets_' + str(wavelet)

    df_trade_table.to_csv(file_name + '_tradeTable' + '.csv')
