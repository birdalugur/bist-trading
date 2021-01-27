#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import mydata
import get_stats

# ## Read data

folder_path = '/home/ugur/bistlmts/data/BIST_Eylul/'

data = mydata.read(folder_path)

# data = pd.read_csv(folder_path)
# data['time'] = pd.to_datetime(data.time)

data = mydata.mid_price(data, agg_time='5Min')

# parameters

pair_names = mydata.pair_names[0:5]
window_size = 300
threshold = 1
intercept = False
w_la8_1 = False

all_results = []

for pair_name in pair_names:
    print(pair_name)
    pair = data.loc[:, pair_name]
    result_std = get_stats.get_stats(pair, window_size, pair_name, threshold, intercept, w_la8_1)
    all_results.append(result_std)
    # try:
    #     result_std = get_stats.get_stats(pair, window_size, pair_name, threshold, intercept, w_la8_1)
    #     all_results.append(result_std)
    # except:
    #     print("hata")


result = pd.concat(all_results)

result.to_csv('rol300_noint_5min_thr2_s1la20.csv')
