import pandas as pd
import datetime
import itertools


def get_file_name(opt):
    file_name = str(opt)
    file_name = file_name.strip("}{")
    file_name = file_name.replace("\'", "")
    file_name = file_name.replace(": ", "_")
    file_name = file_name.replace(", ", "_")
    return file_name


def create_time_range(df):
    day_list = sorted(df.time.dt.date.unique())
    time_list = pd.date_range('7:00:00', '15:00:00', freq='s').time
    day_and_times = [datetime.datetime.combine(i, j) for i in day_list for j in time_list]
    indexes = pd.DatetimeIndex(pd.to_datetime(day_and_times))
    return indexes


def create_bid_ask_mid(pair, data):
    data_pair = data[data['symbol'].isin([pair[0], pair[1]])]
    # print('mp ok!')

    bid_price = data_pair.pivot_table(index='time', columns='symbol', values='bid_price', aggfunc='last')
    ask_price = data_pair.pivot_table(index='time', columns='symbol', values='ask_price', aggfunc='last')
    mid_price = data_pair.pivot_table(index='time', columns='symbol', values='mid_price', aggfunc='mean')
    # print('pivot ok!')
    time_range = create_time_range(data)

    # del (data, folder_path)

    bid_index = bid_price.index.append(time_range).drop_duplicates().sort_values()
    ask_index = ask_price.index.append(time_range).drop_duplicates().sort_values()
    mid_index = mid_price.index.append(time_range).drop_duplicates().sort_values()

    bid_price = bid_price.reindex(bid_index)
    ask_price = ask_price.reindex(ask_index)
    mid_price = mid_price.reindex(mid_index)

    return bid_price, ask_price, mid_price


def multi_opt(mid_freq, window_size, threshold, intercept, wavelet, ln):
    keys = ['mid_freq', 'window_size', 'threshold', 'intercept', 'wavelet', 'ln']

    opt_values = list(itertools.product(mid_freq, window_size, threshold, intercept, wavelet, ln))

    opt_dicts = []

    for opt in opt_values:
        opt_dicts.append(dict(zip(keys, opt)))

    return opt_dicts


def fill_nan(x):
    x = x[:x.last_valid_index()]
    x = x.ffill()
    return x
