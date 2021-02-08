from itertools import combinations
from os import listdir
import glob

import numpy as np
import pandas as pd

BIST30 = ["ARCLK", "ASELS", "BIMAS", "DOHOL", "EKGYO", "FROTO", "HALKB", "GARAN", "ISCTR", "KCHOL", "KOZAA", "KOZAL",
          "KRDMD", "AKBNK", "PETKM", "PGSUS", "SAHOL", "EREGL", "SODA", "TAVHL", "TCELL", "THYAO", "TKFEN",
          "TOASO", "TSKB", "TTKOM", "TUPRS", "VAKBN", "YKBNK"]
# SISE

pair_names = list(combinations(BIST30, 2))


use_cols = ['symbol', 'time', 'bid_price', 'ask_price']

date_columns = 'time'


def is_bist30(x: str) -> bool:
    """
    Is the expression denoted by x a member of bist30?
    """
    for symbol in BIST30:
        if symbol in x:
            return True
    return False


def get_file_paths(path: str) -> list:
    _path = path + '*.csv'
    """
    Args:
        path: verinin okunacağı dizine ait path.

    Returns:
        Dizinde bulunan tüm dosyaların listesi.
        """
    return glob.glob(_path)


def read_multiple_data(all_paths: str) -> pd.DataFrame:
    all_data = []
    for _path in all_paths:
        try:
            all_data.append(
                pd.read_csv(_path, usecols=use_cols,
                            converters={date_columns: lambda x: pd.Timestamp(int(x))})
            )
        except pd.errors.EmptyDataError:
            print("Empty Data:\n", _path)
    return pd.concat(all_data)


def read(path: str, datecol: str = 'time', dt=None) -> pd.DataFrame:
    """
    Bir klasörden csv verilerini okuyun.

    Args:
        path : Klasöre ait yol
        datecol : Datetime column. default 'time'.
    """

    all_paths = map(lambda x: path + x, listdir(path))
    all_data = []
    for _path in all_paths:
        if is_bist30(_path):
            try:
                all_data.append(
                    pd.read_csv(_path,
                                dtype=dt,
                                converters={datecol: lambda x: pd.Timestamp(int(x))})
                )
            except pd.errors.EmptyDataError:
                print("Empty Data:\n", _path)

    return pd.concat(all_data)



def time_range(ask_price, bid_price):
    first_ask = ask_price.index[0]
    last_ask = ask_price.index[-1]
    first_bid = bid_price.index[1]
    last_bid = bid_price.index[-1]

    if (first_ask < first_bid):
        first_time = first_ask
    else:
        first_time = first_bid

    if last_ask > last_bid:
        end_time = last_ask
    else:
        end_time = last_bid

    tr = pd.date_range(first_time, end_time, freq='s')
    tr = pd.DatetimeIndex(tr.to_series().astype('datetime64[s]'))
    return tr
