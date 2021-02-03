#!/usr/bin/env python
# coding: utf-8

import multiprocessing
import pandas as pd
import mydata
import get_stats
from trading_table import trading_table

folder_path = 'data.csv'

# data = mydata.read(folder_path)

data = pd.read_csv(folder_path, parse_dates=['time'], index_col=['time'])
# data['time'] = pd.to_datetime(data.time)

# data = mydata.mid_price(data, agg_time='5Min')

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
    pair = data.loc[:, pair_name]
    pair.dropna(inplace=True)
    stats_rate = get_stats.get_stats(pair, window_size, pair_name, threshold, intercept, wavelet, 'rate')
    stats_100 = get_stats.get_stats(pair, window_size, pair_name, threshold, intercept, wavelet, '100')
    trade_table = trading_table(pair, window_size, pair_name, threshold, intercept, wavelet)

    return stats_rate, stats_100, trade_table


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=8)
    results = pool.map(run, pair_names)

    results = list(zip(*results))

    df_stats_rate = pd.concat(results[0])

    df_stats_100 = pd.concat(results[1])

    df_trade_table = pd.concat(results[2])

    file_name = 'roll_' + str(window_size) + \
                '_freq_' + data_freq + \
                '_thr_' + str(threshold) + \
                '_int_' + str(intercept) + \
                '_wavelets_' + str(wavelet)

    df_stats_rate.to_csv(file_name + '_rate' + '.csv')
    df_stats_100.to_csv(file_name + '_100' + '.csv')
    df_trade_table.to_csv(file_name + '_tradeTable' + '.csv')
