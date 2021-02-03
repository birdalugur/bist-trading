import numpy as np
import pandas as pd
from typing import Union
from itertools import combinations
import random
from importlib import reload

import mydata
import wavelets
import residual
import selling
import rolling


def get_stats(pair, window_size, pair_name, threshold, intercept, w_la8_1, selling_type):
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
    duration_s1 = exit_points_s1 - entry_points_s1
    duration_s2 = exit_points_s2 - entry_points_s2
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Calculation long / short selling (All Returns) >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    return_short_s1 = -selling.calc_selling(pair[pair_name[0]], entry_points_s1, exit_points_s1, selling_type)
    return_long_s1 = selling.calc_selling(pair[pair_name[1]], entry_points_s1, exit_points_s1, selling_type)

    return_short_s2 = -selling.calc_selling(pair[pair_name[1]], entry_points_s2, exit_points_s2, selling_type)
    return_long_s2 = selling.calc_selling(pair[pair_name[0]], entry_points_s2, exit_points_s2, selling_type)

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

    last_total_return = last_total_return_s1.append(last_total_return_s2).sort_index()
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Median >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    median_short_s1 = last_return_short_s1.median()
    median_short_s2 = last_return_short_s2.median()
    median_long_s1 = last_return_long_s1.median()
    median_long_s2 = last_return_long_s1.median()

    median_last_total_return_s1 = last_total_return_s1.median()
    median_last_total_return_s2 = last_total_return_s2.median()

    median_last_total_return = last_total_return.median()
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Cumulative sum >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    c_return_short_s1 = last_return_short_s1.cumsum()
    c_return_long_s1 = last_return_long_s1.cumsum()
    c_return_short_s2 = last_return_short_s2.cumsum()
    c_return_long_s2 = last_return_long_s2.cumsum()
    c_return_s1 = last_total_return_s1.cumsum()
    c_return_s2 = last_total_return_s2.cumsum()

    c_return = c_return_s1[-1] + c_return_s2[-1]
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Average duration >>>>>>>>>>>>>>>>>
    avg_duration_s1 = duration_s1.mean()
    avg_duration_s2 = duration_s2.mean()

    avg_duration = (avg_duration_s1 + avg_duration_s2) / 2
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Median duration >>>>>>>>>>>>>>>>>>>>>>>
    median_duration_s1 = duration_s1.median()
    median_duration_s2 = duration_s2.median()

    duration = duration_s1.append(duration_s2)
    median_duration = duration.median()
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Number of trades >>>>>>>>>>>>>>>>>>>>>>
    number_trade_s1 = len(entry_points_s1)
    number_trade_s2 = len(entry_points_s2)

    number_of_trade = number_trade_s1 + number_trade_s2
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Mean return per trade (CReturn'un en son hanesi/trades) >>>>>>>>>
    mean_return_ls1 = c_return_long_s1[-1] / number_trade_s1
    mean_return_ss1 = c_return_short_s1[-1] / number_trade_s1
    mean_return_ls2 = c_return_long_s2[-1] / number_trade_s2
    mean_return_ss2 = c_return_short_s2[-1] / number_trade_s2
    mean_return_s1 = c_return_s1[-1] / number_trade_s1
    mean_return_s2 = c_return_s2[-1] / number_trade_s2

    mean_c_return = c_return / number_of_trade
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    stats_name = '_'.join(pair_name)

    df_columns = ['c_return', 'number_of_trade', 'mean_c_return', 'median_duration', 'median_last_total_return']
    df_data = [c_return, number_of_trade, mean_c_return, median_duration, median_last_total_return]

    result = pd.DataFrame(data=[df_data], columns=df_columns, index=[stats_name])

    return result
