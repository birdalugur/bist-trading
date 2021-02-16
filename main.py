#!/usr/bin/env python
# coding: utf-8

import multiprocessing
from functools import partial
import pandas as pd

import mydata
from trading_table import trading_table

mid_path = 'mid_price.csv'
bid_path = 'bid_price.csv'
ask_path = 'ask_price.csv'

mid_price = pd.read_csv(mid_path, parse_dates=[0], index_col=0)
bid_price = pd.read_csv(bid_path, parse_dates=[0], index_col=0)
ask_price = pd.read_csv(ask_path, parse_dates=[0], index_col=0)

pair_names = mydata.pair_names


def run(pair_name: str, opt: dict) -> pd.DataFrame:
    print(pair_name)
    window_size = opt['window_size']
    threshold = opt['threshold']
    intercept = opt['intercept']
    wavelet = opt['wavelet']

    pair_mid = mid_price.loc[:, pair_name]

    pair_ask = ask_price.loc[:, pair_name]

    pair_bid = bid_price.loc[:, pair_name]

    trade_table = trading_table(pair_mid, pair_ask, pair_bid, window_size, threshold, intercept, wavelet)

    return trade_table


def parallel_run(core, pairs, opt):
    pool = multiprocessing.Pool(processes=core)
    run_with_opt = partial(run, opt=opt)
    result = pool.map(run_with_opt, pairs)
    return pd.concat(result)


if __name__ == '__main__':
    core = 8
    mid_freq = '5Min', '5Min'
    window_size = 300, 400
    threshold = 1, 2
    intercept = False, True
    wavelet = False, False

    opts = mydata.multi_opt(mid_freq=mid_freq,
                            window_size=window_size,
                            threshold=threshold,
                            intercept=intercept,
                            wavelet=wavelet)

    for opt in opts:
        df_trade_table = parallel_run(core, pair_names, opt)
        file_name = mydata.get_file_name(opt)
        df_trade_table.to_csv(file_name + '_tradeTable' + '.csv', index=False)
