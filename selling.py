import pandas as pd
import numpy as np



def get_signal(x, thresholds=[]):
    signal_1, signal_2 = [], []

    signal1, signal2 = False, False

    prev_sign = 0

    nan_lock = 1

    idx = x.index

    for val, threshold in zip(x, thresholds):

        sign = np.sign(val)

        if abs(val) > threshold:
            nan_lock = 0
            prev_sign = sign
            if sign == 1:
                signal1 = True
                signal2 = False
            else:
                signal1 = False
                signal2 = True
        else:
            if sign == prev_sign:
                pass
            else:
                prev_sign = sign
                signal1 = False
                signal2 = False
            if nan_lock == 1:
                signal1 = np.nan
                signal2 = np.nan
        signal_1.append(signal1)
        signal_2.append(signal2)

    signal_1 = pd.Series(signal_1, index=idx, name='signal_1').replace({False: 0, True: 1})
    signal_2 = pd.Series(signal_2, index=idx, name='signal_2').replace({False: 0, True: 1})

    return signal_1.shift(), signal_2.shift()


def signal_points(signal: pd.Series) -> [pd.Index, pd.Index]:
    """
    Returns the entry and exit_points points of the signal. -> (entry,exit_points)
    """
    entry_exit_points = np.trim_zeros(signal.dropna(), 'f').diff().fillna(1)
    entry_points = entry_exit_points[entry_exit_points == 1].index
    exit_points_points = entry_exit_points[entry_exit_points == -1].index
    if len(entry_points) > len(exit_points_points):
        entry_points = entry_points[0:len(exit_points_points)]
        # exit_points_points = exit_points_points.append(pd.DatetimeIndex([signal.index[-1]]))
    return entry_points, exit_points_points


def get_return(entry_vals, exit_points_vals):
    if len(entry_vals) != len(exit_points_vals):
        print("lengths different - data truncated.")
        n = min([len(entry_vals), len(exit_points_vals)])
        entry_vals = entry_vals.iloc[0:n]
        exit_points_vals = exit_points_vals.iloc[0:n]
    return (exit_points_vals - entry_vals.values) / entry_vals.values


def selling_series(data):
    idx = data.index
    result = []
    _in = 0
    _entry = data.iloc[_in]
    for _out in range(1, len(data)):
        _exit_points = data.iloc[_out]
        # res = (_exit_points - _entry) / _entry
        res = (_exit_points - _entry) * 100
        result.append(res)
    result.insert(0, np.nan)
    result = pd.Series(result, index=idx)
    return result


def time_slice(data, entry, exit_points):
    """
    data: time series"""
    slices = []
    for time in zip(entry, exit_points):
        _slice = data.loc[time[0]:time[1]]
        slices.append(_slice)
    return slices


def calc_selling(data, entry, exit_points):
    all_selling = []
    slices = time_slice(data, entry, exit_points)
    for _slice in slices:
        all_selling.append(selling_series(_slice))
    return pd.concat(all_selling)
