#!/usr/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd
from typing import Union
from itertools import combinations
import statsmodels.api as sm
import random
import plotly.express as px


import mydata
import wavelets
import residual
from get_stats import get_stats

# ## Read data


folder_path = '/home/ugur/bistlmts/data/BIST_Eylul/'


data = mydata.read(folder_path)


# ## Calculate the middle price


data['mid_price'] = (data['bid_price'] + data['ask_price']) / 2

# Create a pivot table using mid price, symbol and time, if two
mid_price = data.pivot_table(
    index='time', columns='symbol', values='mid_price', aggfunc='mean')


# Convert to 1 minute data for every day (agg func = mean, alternatives: median;...)
mid_price = mid_price.groupby(pd.Grouper(
    freq='D')).resample('1Min').mean().droplevel(0)

# fill nan values (ignore end of the day)
mid_price = mid_price.resample('D').apply(
    lambda x: x.apply(lambda x: x[:x.last_valid_index()].ffill()))
mid_price = mid_price.droplevel(0)


# ## Select a pair


pair_name = mydata.pair_names[0]


pair_names = [('ARCLK', 'ASELS'),
              ('ARCLK', 'BIMAS')]


all_results = []

for pair_name in pair_names:

    pair = mid_price.loc[:, pair_name]

    method = 'mra'
    result_mra = get_stats(pair, method, pair_name)
    method = 'std'
    result_std = get_stats(pair, method, pair_name)

    all_results.append(result_mra)
    all_results.append(result_std)

result = pd.concat(all_results)

result.to_csv('resultssss.csv')
