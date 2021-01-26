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
import rolling


def get_stats(pair, window_size, pair_name):
    # ## Select a pair

    threshold_coefficient = 1
    stats_type = 'standart'
    intercept = False
    w_la8_1 = False

    all_windows = rolling.windows(pair, window_size)  # create all windows

    # calculate residuals from windows
    residuals = list(map(lambda w: residual.get_resid(w, intercept=intercept, w_la8_1=w_la8_1), all_windows))

    std = [resid.std() for resid in residuals]

    residuals = pd.concat(map(lambda r: r.tail(1), residuals)).reindex(pair.index)  # get last values

    # Calculate std

    std = pd.Series(std, index=residuals.dropna().index).reindex(pair.index) * threshold_coefficient

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

    fig = plot.trades(residuals, std, trades)
    pd.concat([pair, residuals, std, signal_1, signal_2], axis=1).to_csv('residual.csv')

    # ### Last of trades

    last_return_total = pd.concat(list(map(lambda x: x.tail(1), trades)))

    # ## Cumulative sum

    c_return_total = last_return_total.cumsum()


    duration_trades_mean = pd.Series(duration).mean()

    duration_trades_median = pd.Series(duration).median()

    # ### Number trades

    number_trades = len(trades)

    # ### Mean return per trade (CReturn'un en son hanesi / # trades)

    c_return = c_return_total[-1]

    c_return_per_trade = c_return / number_trades

    # ## Stats Dataframe

    cols = ['c_return', 'c_return_per_trade', 'number_trades', 'duration_trades_mean', 'duration_trades_median']

    stats_name = '_'.join(pair_name) + '_' + stats_type

    stats = pd.DataFrame([[c_return, c_return_per_trade, number_trades, duration_trades_mean, duration_trades_median]
                          ], columns=cols, index=[stats_name],
                         )

    return stats
