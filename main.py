#!/usr/bin/env python
# coding: utf-8
import os
import time
import multiprocessing
import datetime
from functools import partial
import pandas as pd
from itertools import combinations
import numpy as np

from trading_table import trading_table

start = time.time()
folder_path = 'data.csv'


def create_time_range(df):
    day_list = sorted(df.time.dt.date.unique())
    time_list = pd.date_range('7:00:00', '15:00:00', freq='s').time
    day_and_times = [datetime.datetime.combine(i, j) for i in day_list for j in time_list]
    indexes = pd.DatetimeIndex(pd.to_datetime(day_and_times))
    return indexes


def multi_opt(mid_freq, window_size, threshold, intercept, wavelet, ln):
    keys = ['mid_freq', 'window_size', 'threshold', 'intercept', 'wavelet', 'ln']

    try:
        opt_values = list(zip(mid_freq, window_size, threshold, intercept, wavelet, ln))
    except TypeError:
        return dict(zip(keys, [mid_freq, window_size, threshold, intercept, wavelet, ln]))

    opt_dicts = []

    for opt in opt_values:
        opt_dicts.append(dict(zip(keys, opt)))

    return opt_dicts


def get_file_name(opt):
    file_name = str(opt)
    file_name = file_name.strip("}{")
    file_name = file_name.replace("\'", "")
    file_name = file_name.replace(": ", "_")
    file_name = file_name.replace(", ", "_")
    return file_name


data = pd.read_csv(folder_path, parse_dates=['time'])
data = data[data.time.dt.hour < 15]
data['mid_price'] = (data['bid_price'] + data['ask_price']) / 2

print('data ok!')

pair_names = list(combinations(data.symbol.unique(), 2))


def create_bid_ask_mid(pair):
    data_pair = data[data['symbol'].isin([pair[0], pair[1]])]
    # print('mp ok!')

    bid_price = data_pair.pivot_table(index='time', columns='symbol', values='bid_price', aggfunc='last')
    ask_price = data_pair.pivot_table(index='time', columns='symbol', values='ask_price', aggfunc='last')
    mid_price = data_pair.pivot_table(index='time', columns='symbol', values='mid_price', aggfunc='mean')
    # print('pivot ok!')
    time_range = create_time_range(data)

    # del (data, folder_path)

    bid_index = bid_price.index.append(time_range).drop_duplicates().sort_values()
    ask_index = ask_price.index.append(time_range).drop_duplicates().sort_values()
    mid_index = mid_price.index.append(time_range).drop_duplicates().sort_values()

    bid_price = bid_price.reindex(bid_index)
    ask_price = ask_price.reindex(ask_index)
    mid_price = mid_price.reindex(mid_index)

    return bid_price, ask_price, mid_price


def fill_nan(x):
    x = x[:x.last_valid_index()]
    x = x.ffill()
    return x


def run(pair_name: str, opt: dict) -> pd.DataFrame:
    print(pair_name)

    mid_freq = opt['mid_freq']
    window_size = opt['window_size']
    threshold = opt['threshold']
    intercept = opt['intercept']
    wavelet = opt['wavelet']
    ln = opt['ln']

    pair_bid, pair_ask, pair_mid = create_bid_ask_mid(pair_name)
    # pair_mid = mid_price.loc[:, iter]
    pair_mid = pair_mid.groupby(pd.Grouper(freq='D')).resample(mid_freq).mean().droplevel(0)
    pair_mid = pair_mid.resample('D').apply(fill_nan).droplevel(0)
    pair_mid = pair_mid.resample('D').apply(fill_nan).droplevel(0)

    if ln:
        pair_mid = np.log(pair_mid)

    # pair_ask = ask_price.loc[:, pair_name]
    pair_ask = pair_ask.resample('D').apply(fill_nan).droplevel(0)

    # pair_bid = bid_price.loc[:, pair_name]
    pair_bid = pair_bid.resample('D').apply(fill_nan).droplevel(0)

    pair_mid.dropna(inplace=True)
    pair_ask.dropna(inplace=True)
    pair_bid.dropna(inplace=True)

    trade_table = trading_table(pair_mid, pair_ask, pair_bid, window_size, threshold, intercept, wavelet)
    return trade_table


def parallel_run(core, pairs, opt):
    pool = multiprocessing.Pool(processes=core)
    run_with_opt = partial(run, opt=opt)
    result = pool.map(run_with_opt, pairs)
    return pd.concat(result)


if __name__ == '__main__':
    core = 32
    mid_freq = '5Min'
    window_size = 300
    threshold = 1
    intercept = False
    wavelet = False
    ln = True

    opts = multi_opt(mid_freq=mid_freq,
                     window_size=window_size,
                     threshold=threshold,
                     intercept=intercept,
                     wavelet=wavelet,
                     ln=ln)
    if isinstance(opts, dict):
        opt = opts
        df_trade_table = parallel_run(core, pair_names, opt)
        file_name = get_file_name(opt)
        df_trade_table.to_csv(file_name + '_tradeTable' + '.csv', index=False)
    else:
        for opt in opts:
            df_trade_table = parallel_run(core, pair_names, opt)
            file_name = get_file_name(opt)
            df_trade_table.to_csv(file_name + '_tradeTable' + '.csv', index=False)
print(time.time() - start)
