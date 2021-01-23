import numpy as np
import pandas as pd
from typing import Union
from itertools import combinations
import statsmodels.api as sm
import random
import plotly.express as px
from wavelets import mra_s1


def residuals(first, second, intercept=False):
    first_symbol = first.values.reshape(-1, 1)
    second_symbol = second.values.reshape(-1, 1)
    if intercept:
        first_symbol = sm.add_constant(first)
    model = sm.OLS(second_symbol, first_symbol).fit()
    resid = pd.Series(model.resid)
    return resid


def get_resid(pair, intercept=False, w_la8_1=False):
    first = pair.iloc[:, 0]
    second = pair.iloc[:, 1]

    name = '_'.join((first.name, second.name))

    if w_la8_1:
        first = mra_s1(first)
        second = mra_s1(second)

    resids = residuals(first, second, intercept)
    resids.name = name
    return resids



def rollPair(pair, window, intercept=False, w_la8_1=False):
    start = 0
    lenght = len(pair) - window + 1
    end = window
    name = '_'.join(pair.columns)
    all_idx = []
    all_values = []

    for i in range(window - 1):
        all_values.append(None)
        all_idx.append(pair.index[i])

    for i in range(lenght):
        item = pair[start:end]
        idx = item.index[-1]
        value = get_resid(item, intercept, w_la8_1).tail(1).values[0]

        start = start + 1
        end = end + 1

        all_idx.append(idx)
        all_values.append(value)

    return pd.Series(all_values, index=all_idx, name=name)


def rollPair2(pair, window: pd.DateOffset, agg_func='last', intercept=False, w_la8_1=False):
    window_times = rolling_times(pair.index, window)
    result_times = []
    result_values = []
    for time in window_times:
        start = time[0]
        end = time[1]
        result_times.append(end)
        _residuals = get_resid(pair.loc[start:end], intercept, w_la8_1)
        _residual = apply_func(_residuals, agg_func)
        result_values.append(_residual)
    results = pd.Series(data=result_values, index=result_times).reindex(pair.index)

    return results


def apply_func(data: pd.Series, func: str) -> float:
    if func == 'last':
        return data.tail(1).values[0]


def rolling_times(time_series: pd.DatetimeIndex, window: pd.DateOffset):
    """Creates time pairs for the rolling operation."""
    start_times = time_series.drop(time_series.to_series().last(window))
    end_times = start_times + window
    return list(zip(start_times, end_times))



def expand(pair, window=pd.DateOffset(minutes=5), intercept=False, w_la8_1=False):
    window_type = window.kwds.popitem()[0]
    window_val = window.kwds.popitem()[1]  # window değeri

    date = pair.index[0].date()  # başlangıç tarihi

    finish = pair.index[-1]  # bitiş zamanı

    start_time = pair.index[0]  # dizinin başlangıç zamanı

    end_time = start_time + window

    resid_list = []
    time_list = []

    for i in range(window_val):
        resid_list.append(None)
        time_list.append(pair.index[i])

    while True:
        if end_time > finish:
            break
        data = pair[start_time:end_time]

        if data.size != 0:
            resid = get_resid(data, intercept, w_la8_1).iloc[-1]
            resid_list.append(resid)
            time_list.append(end_time)

        end_time = end_time + pd.DateOffset(minutes=1)

        if end_time > date:
            start_time = end_time - window
            date = end_time.date()

    return pd.Series(resid_list, index=time_list)
