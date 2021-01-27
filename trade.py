#!/usr/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd
from typing import Union
from itertools import combinations
import statsmodels.api as sm
import random
import plotly.express as px
from importlib import reload

import mydata
import wavelets
import residual
import selling
import rolling
import plot

# ## Read data

folder_path = '/home/ugur/bistlmts/data/BIST_Eylul/'

data = mydata.read(folder_path)

data = mydata.mid_price(data, agg_time='5Min')

# ## Select a pair

pair_name = mydata.pair_names[9]
pair = data.loc[:, pair_name]

window_size = 100
threshold = 1

stats_type = 'standart'
intercept = False
w_la8_1 = False

all_windows = rolling.windows(pair, window_size)  # create all windows

# calculate residuals from windows
residuals = list(map(lambda w: residual.get_resid(w, intercept=intercept, w_la8_1=w_la8_1), all_windows))

std = [resid.std() for resid in residuals]

residuals = pd.concat(map(lambda r: r.tail(1), residuals))  # get last values

# Calculate std

std = pd.Series(std, index=residuals.index)

residuals = residuals.dropna().reindex(pair.index)
std = std.dropna().reindex(pair.index) * threshold

# Find signals

signal_1, signal_2 = selling.get_signal(residuals, std)

all_signal = pd.Series([i or j for i, j in zip(signal_1, signal_2)], index=signal_1.index)

# Mark entry - exit points

entry_points_s1, exit_points_1 = selling.signal_points(signal_1)

entry_points_s2, exit_points_2 = selling.signal_points(signal_2)

entry_points, exit_points = selling.signal_points(all_signal)

entry_exit = list(zip(entry_points, exit_points))

# ## Calculation long / short selling


return_short_s1 = -selling.calc_selling(pair[pair_name[0]], entry_points_s1, exit_points_1)

return_long_s1 = selling.calc_selling(pair[pair_name[1]], entry_points_s1, exit_points_1)

return_short_s2 = selling.calc_selling(pair[pair_name[0]], entry_points_s2, exit_points_2)

return_long_s2 = -selling.calc_selling(pair[pair_name[1]], entry_points_s2, exit_points_2)

return_s1 = return_short_s1 + return_long_s1

return_s2 = return_short_s2 + return_long_s2

return_total = return_s1.append(return_s2).sort_index()

# All Trades

returns = return_total.dropna()

trades = []

for start, end in entry_exit:
    trades.append(returns.loc[start:end])

duration = [end - start for start, end in entry_exit]


# pd.concat([pair, residuals, std, signal_1, signal_2], axis=1).to_csv('residual.csv')


# ## Last of Trades

def get_trade_number(x):
    """Her bir trade'i numaralandır, NaN'ları hariç tutar."""
    return (~(x.isna().cumsum()[x.notna()].duplicated())).cumsum()


def last_of_trade(trade):
    trade_number = trade.to_frame().assign(number=get_trade_number(trade)).reset_index()
    return trade_number.groupby('number').last()


last_return_short_s1 = last_of_trade(return_short_s1)
last_return_long_s1 = last_of_trade(return_long_s1)
last_return_short_s2 = last_of_trade(return_short_s2)
last_return_long_s2 = last_of_trade(return_long_s2)

# ### Number of trades


# trade bitimi-time series
get_number = lambda x: x['time'].reset_index().set_index('time')['number']

lastnumber_return_1 = get_number(last_return_short_s1)
lastnumber_return_2 = get_number(last_return_short_s2)

number_return_1 = get_trade_number(return_long_s1)
number_return_2 = get_trade_number(return_long_s2)

# ### Last of trades


last_return_short_s1 = last_return_short_s1.set_index('time').iloc[:, -1].rename('last_return_short_s1')
last_return_long_s1 = last_return_long_s1.set_index('time').iloc[:, -1].rename('last_return_long_s1')
last_return_short_s2 = last_return_short_s2.set_index('time').iloc[:, -1].rename('last_return_short_s2')
last_return_long_s2 = last_return_long_s2.set_index('time').iloc[:, -1].rename('last_return_long_s2')

last_return_s1 = last_return_short_s1 + last_return_long_s1
last_return_s2 = last_return_short_s2 + last_return_long_s2

last_return_total = pd.concat(list(map(lambda x: x.tail(1), trades)))

# ## Cumulative sum


c_return_short_s1 = last_return_short_s1.cumsum()
c_return_long_s1 = last_return_long_s1.cumsum()

c_return_short_s2 = last_return_short_s2.cumsum()
c_return_long_s2 = last_return_long_s2.cumsum()

c_return_s1 = c_return_short_s1 + c_return_long_s1
c_return_s2 = c_return_short_s2 + c_return_long_s2

c_return_total = last_return_total.cumsum()


fig = plot.trades(residuals, std, trades, pair_name, c_return_total * 10)


# ## Stats

# ### Median return per trade


median_short_s1 = last_return_short_s1.median()
median_short_s2 = last_return_short_s2.median()
median_long_s1 = last_return_long_s1.median()
median_long_s2 = last_return_long_s1.median()

median_s1 = last_return_s1.median()
median_s2 = last_return_s2.median()

median_total = last_return_total.median()

# ### Average duration of trades


duration_s1 = exit_points_1 - entry_points_s1[0:len(exit_points_1)]
duration_s2 = exit_points_2 - entry_points_s2[0:len(exit_points_2)]
avg_duration_s1 = duration_s1.seconds.to_series().mean()
avg_duration_s2 = duration_s2.seconds.to_series().mean()

duration_trades_mean = pd.Series(duration).mean()

# ### Median duration of trades


median_duration_s1 = duration_s1.median()
median_duration_s2 = duration_s2.median()

duration_trades_median = pd.Series(duration).median()

# ### Number trades


number_trades = len(trades)

# ### Mean return per trade (CReturn'un en son hanesi / # trades)


mean_cs1 = c_return_s1[-1] / len(c_return_s1)
mean_cs2 = c_return_s2[-1] / len(c_return_s2)

c_return = c_return_total[-1]

c_return_per_trade = c_return / number_trades

# ## Stats Dataframe


cols = ['c_return', 'c_return_per_trade', 'number_trades', 'duration_trades_mean', 'duration_trades_median']

stats_name = '_'.join(pair_name) + '_' + stats_type

stats = pd.DataFrame([[c_return, c_return_per_trade, number_trades, duration_trades_mean, duration_trades_median]
                      ], columns=cols, index=[stats_name],
                     )

stats
