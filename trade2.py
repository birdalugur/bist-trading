#!/usr/bin/env python
# coding: utf-8

import pandas as pd

import mydata
import residual
import selling
import rolling
import plot
from buysell import buy_sell_stats

# Read data & calc mp >>>>>>>>>>>>>>>>>>>>>>
folder_path = '/home/ugur/bistlmts/data/BIST_Eylul/'
data = mydata.read(folder_path)
data = mydata.mid_price(data, agg_time='5Min')
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

data = pd.read_csv('data.csv', parse_dates=['time'], index_col=['time'])


# Select a pair >>>>>>>>>>>>>>>>>>>
pair_name = mydata.pair_names[1]
pair = data.loc[:, pair_name]
pair.dropna(inplace=True)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# Options >>>>>>>>>>>>>>>>>>>>>>>>
window_size = 300
threshold = 1
stats_type = 'standart'
intercept = False
w_la8_1 = False
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# calculate residuals & std from windows >>>>>>>>>>>>>>>>>>>>>>>>>>
all_windows = rolling.windows(pair, window_size)
residuals = list(map(lambda w: residual.get_resid(w, intercept=intercept, w_la8_1=w_la8_1), all_windows))
std = [resid.std() for resid in residuals]
residuals = pd.concat(map(lambda r: r.tail(1), residuals))  # get last values
std = pd.Series(std, index=residuals.index)
residuals = residuals.dropna().reindex(pair.index)
std = std.dropna().reindex(pair.index) * threshold
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# Find signals >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
signal_1, signal_2 = selling.get_signal(residuals, std)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# Mark entry - exit points >>>>>>>>>>>>>>>>>>>>>>>>>
entry_points_s1, exit_points_s1 = selling.signal_points(signal_1)
entry_points_s2, exit_points_s2 = selling.signal_points(signal_2)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# Duration >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
duration_s1 = exit_points_s1-entry_points_s1
duration_s2 = exit_points_s2-entry_points_s2
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# Calculation long / short selling >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
return_short_s1 = -selling.calc_selling(pair[pair_name[0]], entry_points_s1, exit_points_s1)
return_long_s1 = selling.calc_selling(pair[pair_name[1]], entry_points_s1, exit_points_s1)

return_short_s2 = -selling.calc_selling(pair[pair_name[1]], entry_points_s2, exit_points_s2)
return_long_s2 = selling.calc_selling(pair[pair_name[0]], entry_points_s2, exit_points_s2)

total_return_s1 = return_short_s1 + return_long_s1
total_return_s2 = return_short_s2 + return_long_s2
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# Last of trade >>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def get_trade_number(x):
    """Her bir trade'i numaralandır, NaN'ları hariç tutar."""
    return (~(x.isna().cumsum()[x.notna()].duplicated())).cumsum()


def last_of_trade(trade, name):
    trade_number = trade.to_frame().assign(number=get_trade_number(trade)).reset_index()
    result = trade_number.groupby('number').last().set_index('time').iloc[:, -1]
    return result.rename(name)


last_return_short_s1 = last_of_trade(return_short_s1, 'return_short_s1')
last_return_long_s1 = last_of_trade(return_long_s1, 'return_long_s1')
last_return_short_s2 = last_of_trade(return_short_s2, 'return_short_s2')
last_return_long_s2 = last_of_trade(return_long_s2, 'return_long_s2')

last_total_return_s1 = last_of_trade(total_return_s1, 'total_return_s1')
last_total_return_s2 = last_of_trade(total_return_s2, 'total_return_s2')
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<



# Median >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
median_short_s1 = last_return_short_s1.median()
median_short_s2 = last_return_short_s2.median()
median_long_s1 = last_return_long_s1.median()
median_long_s2 = last_return_long_s1.median()

median_last_total_return_s1 = last_total_return_s1.median()
median_last_total_return_s2 = last_total_return_s2.median()
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<




# Cumulative sum >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
c_return_short_s1 = last_return_short_s1.cumsum()
c_return_long_s1 = last_return_long_s1.cumsum()
c_return_short_s2 = last_return_short_s2.cumsum()
c_return_long_s2 = last_return_long_s2.cumsum()
c_return_s1 = last_total_return_s1.cumsum()
c_return_s2 = last_total_return_s2.cumsum()
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<






# Average duration >>>>>>>>>>>>>>>>>
avg_duration_s1 = duration_s1.mean()
avg_duration_s2 = duration_s2.mean()
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# Median duration >>>>>>>>>>>>>>>>>>>>>>>
median_duration_s1 = duration_s1.median()
median_duration_s2 = duration_s2.median()
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<



# Number of trades >>>>>>>>>>>>>>>>>>>>>>
length_s1 = len(entry_points_s1)
length_s2 = len(entry_points_s2)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<




# Mean return per trade (CReturn'un en son hanesi/trades) >>>>>>>>>
mean_return_ls1 = c_return_long_s1[-1]/length_s1
mean_return_ss1 = c_return_short_s1[-1]/length_s1
mean_return_ls2 = c_return_long_s2[-1]/length_s2
mean_return_ss2 = c_return_short_s2[-1]/length_s2
mean_return_s1 = c_return_s1[-1]/length_s1
mean_return_s2 = c_return_s2[-1]/length_s2
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<





# Results >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
stats_name = '_'.join(pair_name)

df_columns = ['avg_duration', 'median_duration', 'length', 'avg_cum_return_long', 'avg_cum_return_short',
              'avg_return', 'median_short', 'median_long', 'median_return']

df_index = pd.MultiIndex.from_arrays([[stats_name, stats_name], ['signal_1', 'signal_2']])

df_data = [
    [avg_duration_s1, median_duration_s1, length_s1, mean_return_ls1,
     mean_return_ss1, mean_return_s1, median_short_s1, median_long_s1, median_last_total_return_s1],

    [avg_duration_s2, median_duration_s2, length_s2, mean_return_ls2,
     mean_return_ss2, mean_return_s2, median_short_s2, median_long_s2, median_last_total_return_s2]
]

result = pd.DataFrame(data=df_data, columns=df_columns, index=df_index)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<











