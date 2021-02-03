#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import mydata
import get_stats
import multiprocessing

# ## Read data

folder_path = '/home/ugur/bistlmts/data/BIST_Eylul/'

data = mydata.read(folder_path)

# data = pd.read_csv(folder_path)
# data['time'] = pd.to_datetime(data.time)

data = mydata.mid_price(data, agg_time='5Min')

# parameters

pair_names = mydata.pair_names
window_size = 300
threshold = 1
intercept = False
w_la8_1 = False

all_stats = []
all_buy_sell = []


def run(pair_name):
    print(pair_name)
    pair = data.loc[:, pair_name]
    pair.dropna(inplace=True)
    stats, buy_sell = get_stats.get_stats(pair, window_size, pair_name, threshold, intercept, w_la8_1)

    return stats, buy_sell


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=8)
    results = pool.map(run, pair_names)

    results = list(zip(*results))

    df_stats = pd.concat(results[0])
    df_buy_sell = pd.concat(results[1])

    df_stats.to_csv('rol300_noint_5min_thr1_std.csv')
    df_buy_sell.to_csv('bs_rol300_noint_5min_thr1_std.csv')
