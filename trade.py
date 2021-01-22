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
import selling

# ## Read data


folder_path = '/home/ugur/bistlmts/data/BIST_Eylul/'

data = mydata.read(folder_path)

# ## Calculate the middle price


data['mid_price'] = (data['bid_price'] + data['ask_price']) / 2

# Create a pivot table using mid price, symbol and time, if two
mid_price = data.pivot_table(index='time', columns='symbol', values='mid_price', aggfunc='mean')

# Convert to 1 minute data for every day (agg func = mean, alternatives: median;...)
mid_price = mid_price.groupby(pd.Grouper(freq='D')).resample('1Min').mean().droplevel(0)

# fill nan values (ignore end of the day)
mid_price = mid_price.resample('D').apply(lambda x: x.apply(lambda x: x[:x.last_valid_index()].ffill()))
mid_price = mid_price.droplevel(0)

# ## Select a pair


pair_name = mydata.pair_names[0]

pair = mid_price.loc[:, pair_name]

method = 'std'

residuals = residual.rollPair(pair, 50, intercept=False, w_la8_1=True)
residuals = residual.expand(pair, window=pd.DateOffset(minutes=5), intercept=False, w_la8_1=True)
# ## Calculate std


std = residuals.rolling(window=50, min_periods=0).std().rename('std')

# ## Find signals


signal_1, signal_2 = selling.get_signal(residuals, std)

all_signal = pd.Series([i or j for i, j in zip(signal_1, signal_2)], index=signal_1.index)

# ## Mark entry - exit points


entry_points_s1, exit_points_1 = selling.signal_points(signal_1)

entry_points_s2, exit_points_2 = selling.signal_points(signal_2)

entry_points, exit_points = selling.signal_points(all_signal)

entry_points = entry_points[0:len(exit_points)]

entry_exit = list(zip(entry_points, exit_points))

# ## Calculation long / short selling


return_short_s1 = -selling.calc_selling(pair[pair_name[0]], entry_points_s1, exit_points_1)

return_long_s1 = selling.calc_selling(pair[pair_name[1]], entry_points_s1, exit_points_1)

return_short_s2 = selling.calc_selling(pair[pair_name[0]], entry_points_s2, exit_points_2)

return_long_s2 = -selling.calc_selling(pair[pair_name[1]], entry_points_s2, exit_points_2)

return_s1 = return_short_s1 + return_long_s1

return_s2 = return_short_s2 + return_long_s2

return_total = return_s1.append(return_s2).sort_index()

# ## All Trades


returns = return_total.dropna()

trades = []

for start, end in entry_exit:
    trades.append(returns.loc[start:end])

duration = [end - start for start, end in entry_exit]

# ## Last of Trades


# Her bir trade'i numaralandır, NaN'ları hariç tutar
get_trade_number = lambda x: (~(x.isna().cumsum()[x.notna()].duplicated())).cumsum()


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

stats_name = '_'.join(pair_name) + '_std'

stats = pd.DataFrame([[c_return, c_return_per_trade, number_trades, duration_trades_mean, duration_trades_median]
                      ], columns=cols, index=[stats_name],
                     )

stats

# ## Visualize results


import plotly.graph_objects as go

bar = go.Figure(go.Bar(name='last trade', x=last_return_total.index, y=last_return_total.values))

bar.show()

# ### Cumulative return


fig_ctotal = go.Figure()

fig_ct = go.Scatter(x=c_return_total.index, y=c_return_total, mode='lines', name='total cumulative return')

fig_ctotal.add_trace(fig_ct)
fig_ctotal.show()

# fig_cum_return = go.Figure()
#
# fig_s1 = go.Scatter(x=c_return_s1.index, y=c_return_s1, mode='lines', name='cumulative return s1')
#
# fig_s2 = go.Scatter(x=c_return_s2.index, y=c_return_s2, mode='lines', name='cumulative return s2')
#
# fig_cum_return.update_layout(xaxis_title='time', yaxis_title='cumulative return')
#
# fig_cum_return.add_traces([fig_s1, fig_s2])
#
# fig_cum_return.show()

# # Variables
# # ---------
# 
# pair,    # mid price
# residual,
# std, 
# signal_1,
# signal_2,
# 
# # Tradelerin başlangıç ve bitişini gösteren DatetimeIndex.
# entry_points_s1,
# entry_points_s2,
# exit_points_1,
# exit_points_2,
# 
# # (exit-entry)/entry ile hesaplanmış tüm returnler.
# return_short_s1,
# return_short_s2,
# return_long_s1,
# return_long_s2,
# 
# return_s1,
# return_s2,
# return_total,
# 
# # Last of trades.
# last_return_short_s1,
# last_return_long_s1,
# last_return_short_s2,
# last_return_long_s2,
# 
# last_return_s1,   # last_return_short_s1+last_return_long_s1
# last_return_s2,
# last_return_total,
# 
# # Number of trades
# lastnumber_return_1,
# lastnumber_return_2,
# 
# number_return_1,
# number_return_2,
# 
# # Cumulative
# c_return_short_s1,
# c_return_long_s1,
# c_return_short_s2,
# c_return_long_s2,
# 
# c_return_s1, # c_return_short_s1 + c_return_long_s1
# c_return_s2,
# c_return_total,
# 
# # Median
# median_s1,
# median_s2,
# median_total,
# 
# median_duration_s1,
# median_duration_s2,
# 
# # Mean
# mean_ctotal,
# mean_cs1,
# mean_cs2,
# 
# avg_duration_s1,
# avg_duration_s2
# 
# None
