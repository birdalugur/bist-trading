#!/usr/bin/env python
# coding: utf-8

import time
import multiprocessing
from functools import partial
import pandas as pd
from itertools import combinations, permutations
import datetime

from trading_table import trading_table
import auxiliary as aux
import signals

start = time.time()
folder_path = 'test_data.csv'

data = pd.read_csv(folder_path, parse_dates=['time'])
# data.time = data.time.apply(lambda x: pd.Timestamp(int(x)))

data = data[data.time.dt.time >= datetime.time(7, 00, 00)]
data = data[data.time.dt.time <= datetime.time(14, 55, 00)]

reverse = False

pair_names = list(combinations(data.symbol.unique(), 2))

if reverse:
    all_pairs = list(permutations(data.symbol.unique(), 2))
    pair_names = list(set(all_pairs) - set(pair_names))

pair_names = [('BIMAS', 'AKBNK')]


def run(pair_name: str, opt: dict, signal_func) -> pd.DataFrame:
    print(pair_name)
    mid_freq = opt['mid_freq']
    window_size = opt['window_size']
    coeff_negative = opt['coeff_negative']
    coeff_positive = opt['coeff_positive']
    intercept = opt['intercept']
    wavelet = opt['wavelet']
    ln = opt['ln']

    pair_bid, pair_ask, pair_mid = aux.create_bid_ask_mid(pair_name, data)

    pair_bid, pair_ask, pair_mid = aux.convert_bid_ask_mid(pair_bid, pair_ask, pair_mid, mid_freq, ln)

    trade_table = trading_table(pair_mid, pair_ask, pair_bid, window_size, coeff_negative, coeff_positive, intercept,
                                wavelet, signal_func, mid_freq)
    return trade_table


def parallel_run(core, pairs, opt, signal_func):
    pool = multiprocessing.Pool(processes=core)
    run_with_opt = partial(run, opt=opt, signal_func=signal_func)
    result = pool.map(run_with_opt, pairs)
    return pd.concat(result)


if __name__ == '__main__':
    core = 8
    mid_freq = '5Min',
    window_size = 300,
    # threshold = 1,
    coeff_negative = 1,
    coeff_positive = 1,
    intercept = False,
    wavelet = False,
    ln = False,

    signal_func = signals.get_signal3

    opts = aux.multi_opt(mid_freq=mid_freq,
                         window_size=window_size,
                         coeff_negative=coeff_negative,
                         coeff_positive=coeff_positive,
                         intercept=intercept,
                         wavelet=wavelet,
                         ln=ln)

    if len(pair_names) == 1:
        df_trade_table = run(pair_names[0], opts[0], signal_func)
        file_name = aux.get_file_name(opts[0]) + '_signalFunc_' + signal_func.__name__
        df_trade_table.to_csv(file_name + '_tradeTable' + '.csv', index=False)
    else:
        if isinstance(opts, dict):
            opt = opts
            df_trade_table = parallel_run(core, pair_names, opt, signal_func)
            file_name = aux.get_file_name(opt) + '_signalFunc_' + signal_func.__name__
            df_trade_table.to_csv(file_name + '_tradeTable' + '.csv', index=False)
        else:
            for opt in opts:
                df_trade_table = parallel_run(core, pair_names, opt, signal_func)
                file_name = aux.get_file_name(opt) + '_signalFunc_' + signal_func.__name__
                df_trade_table.to_csv(file_name + '_tradeTable' + '.csv', index=False)
print(time.time() - start)
