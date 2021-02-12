#!/usr/bin/env python
# coding: utf-8

import multiprocessing
from functools import partial
import pandas as pd

import mydata
from trading_table import trading_table



folder_path = 'data/201911.csv'

cols = ['symbol', 'time', 'bid_price', 'ask_price']

data = pd.read_csv(folder_path, converters={'time': lambda x: pd.Timestamp(int(x))}, usecols=cols)

data = data[data.symbol.isin(mydata.BIST30)]

data = data.set_index('time')

data['mid_price'] = data['bid_price'] + data['ask_price']

mid_price = data.pivot_table(index='time', columns='symbol', values='mid_price', aggfunc='mean')
bid_price = data.pivot_table(index='time', columns='symbol', values='bid_price', aggfunc='last')
ask_price = data.pivot_table(index='time', columns='symbol', values='ask_price', aggfunc='last')

del (data, folder_path)

time_range = mydata.time_range(ask_price, bid_price)

mid_index = mid_price.index.append(time_range).drop_duplicates().sort_values()
bid_index = bid_price.index.append(time_range).drop_duplicates().sort_values()
ask_index = ask_price.index.append(time_range).drop_duplicates().sort_values()

mid_price = mid_price.reindex(mid_index)
bid_price = bid_price.reindex(bid_index)
ask_price = ask_price.reindex(ask_index)

del (ask_index, bid_index, mid_index, time_range)


def fill_nan(x):
    x = x[:x.last_valid_index()]
    x = x.ffill()
    return x


pair_names = mydata.pair_names[0:3]


def run(pair_name: str, opt: dict) -> pd.DataFrame:
    print(pair_name)

    mid_freq = opt['mid_freq']
    window_size = opt['window_size']
    threshold = opt['threshold']
    intercept = opt['intercept']
    wavelet = opt['wavelet']

    pair_mid = mid_price.loc[:, pair_name]
    pair_mid = pair_mid.groupby(pd.Grouper(freq='D')).resample(mid_freq).mean().droplevel(0)
    pair_mid = pair_mid.resample('D').apply(fill_nan).droplevel(0)

    pair_ask = ask_price.loc[:, pair_name]
    pair_ask = pair_ask.resample('D').apply(fill_nan).droplevel(0)

    pair_bid = bid_price.loc[:, pair_name]
    pair_bid = pair_bid.resample('D').apply(fill_nan).droplevel(0)

    pair_mid.dropna(inplace=True)
    pair_ask.dropna(inplace=True)
    pair_bid.dropna(inplace=True)

    trade_table = trading_table(pair_mid, pair_ask, pair_bid, window_size, threshold, intercept, wavelet)

    return trade_table



if __name__ == '__main__':
    mid_freq = '5Min', '5Min', '10Min'
    window_size = 300, 500, 400
    threshold = 1, 2, 3
    intercept = False, True, True
    wavelet = False, True, False

    opts = mydata.multi_opt(mid_freq=mid_freq,
                            window_size=window_size,
                            threshold=threshold,
                            intercept=intercept,
                            wavelet=wavelet)

    pool = multiprocessing.Pool(processes=8)

    for opt in opts:
        run_with_opt = partial(run, opt=opt)

        results = pool.map(run_with_opt, pair_names)
        df_trade_table = pd.concat(results)

        file_name = mydata.get_file_name(opt)
        df_trade_table.to_csv(file_name + '_tradeTable' + '.csv', index=False)

