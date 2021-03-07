import pandas as pd
import numpy as np
import signals


# def get_return(entry_vals, exit_points_vals):
#     if len(entry_vals) != len(exit_points_vals):
#         print("lengths different - data truncated.")
#         n = min([len(entry_vals), len(exit_points_vals)])
#         entry_vals = entry_vals.iloc[0:n]
#         exit_points_vals = exit_points_vals.iloc[0:n]
#     return (exit_points_vals - entry_vals.values) / entry_vals.values


def selling_series(data):
    idx = data.index
    result = []
    _in = 0
    _entry = data.iloc[_in]
    for _out in range(1, len(data)):
        _exit_points = data.iloc[_out]
        res = (_exit_points - _entry) / _entry
        result.append(res)
    result.insert(0, np.nan)
    result = pd.Series(result, index=idx)
    return result


def selling_series_100(data):
    idx = data.index
    result = []
    _in = 0
    _entry = data.iloc[_in]
    for _out in range(1, len(data)):
        _exit_points = data.iloc[_out]
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


def calc_selling(data, entry, exit_points, type):
    all_selling = []
    slices = time_slice(data, entry, exit_points)
    if type == 'rate':
        for _slice in slices:
            all_selling.append(selling_series(_slice))
    elif type == '100':
        for _slice in slices:
            all_selling.append(selling_series_100(_slice))
    else:
        raise ValueError
    return pd.concat(all_selling)


def get_return(ask_price, bid_price, mid_price, all_signals, return_type='rate', freq='5Min'):
    def get_first_prices(ts, points, freq=freq):
        """Verilen zamana ait ilk işlemi döndürür. İşlem yoksa NaN kabul edilir."""

        new_ts = pd.DataFrame(columns=ts.columns)
        ts = ts.dropna()
        up_time = pd.Timedelta(freq) - pd.Timedelta(nanoseconds=1)

        for point in points:
            start_time = pd.Timestamp(point)
            end_time = start_time + up_time
            x = ts.loc[start_time:end_time]
            x = x.dropna()

            if len(x) == 0:
                be_added = pd.DataFrame(columns=ts.columns, index=[point])
            else:
                be_added = x.head(1)
                be_added.index = [point]
            new_ts = new_ts.append(be_added)

        return new_ts

    idx = mid_price.index
    ask_price = get_first_prices(ask_price, idx)

    bid_price = get_first_prices(bid_price, idx)

    signal_1, signal_2 = all_signals['signal1'], all_signals['signal2']

    # Mark entry - exit points >>>>>>>>>>>>>>>>>>>>>>>>>
    entry_points_s1, exit_points_s1 = signals.signal_points(signal_1)
    entry_points_s2, exit_points_s2 = signals.signal_points(signal_2)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Calculation long / short returns (All Returns) >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    return_short_s1 = -calc_selling(bid_price.iloc[:, 0], entry_points_s1, exit_points_s1, return_type)
    return_long_s1 = calc_selling(ask_price.iloc[:, 1], entry_points_s1, exit_points_s1, return_type)

    return_long_s2 = calc_selling(ask_price.iloc[:, 0], entry_points_s2, exit_points_s2, return_type)
    return_short_s2 = -calc_selling(bid_price.iloc[:, 1], entry_points_s2, exit_points_s2, return_type)

    total_return_s1 = return_short_s1 + return_long_s1
    total_return_s2 = return_short_s2 + return_long_s2

    total_return = total_return_s1.append(total_return_s2).sort_index()

    total_return.dropna(inplace=True)

    return total_return

