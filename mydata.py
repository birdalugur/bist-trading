import numpy as np
import pandas as pd
from typing import Union
from itertools import combinations
import statsmodels.api as sm
import random
import plotly.express as px

BIST30 = ["ARCLK", "ASELS", "BIMAS", "DOHOL", "EKGYO", "FROTO", "HALKB", "GARAN", "ISCTR", "KCHOL", "KOZAA", "KOZAL",
          "KRDMD", "AKBNK", "PETKM", "PGSUS", "SAHOL", "EREGL", "SODA", "TAVHL", "TCELL", "THYAO", "TKFEN",
          "TOASO", "TSKB", "TTKOM", "TUPRS", "VAKBN", "YKBNK"]
# SISE

pair_names = list(combinations(BIST30, 2))


def is_bist30(x: str) -> bool:
    """
    Is the expression denoted by x a member of bist30?
    """
    for symbol in BIST30:
        if symbol in x:
            return True
    return False


def read(path: str, datecol: str = 'time', dt=None) -> pd.DataFrame:
    """
    Bir klasörden csv verilerini okuyun.

    Args:
        path : Klasöre ait yol
        datecol : Datetime column. default 'time'.
    """
    from os import listdir

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


def mid_price(data: pd.DataFrame, agg_time: str = '1Min') -> pd.DataFrame:
    """
    Calculate mid price.

    Args:
        index: 'time'
        columns: 'symbol'
        values: 'mid_price'
        aggfunc: 'mean'
    """
    data['mid_price'] = (data['bid_price'] + data['ask_price']) / 2

    # Create a pivot table using mid price, symbol and time, if two
    mid_price = data.pivot_table(index='time', columns='symbol', values='mid_price', aggfunc='mean')

    # Convert to 1 minute data for every day (agg func = mean, alternatives: median;...)
    mid_price = mid_price.groupby(pd.Grouper(freq='D')).resample(agg_time).mean().droplevel(0)

    # fill nan values (ignore end of the day)
    mid_price = mid_price.resample('D').apply(lambda x: x.apply(lambda x: x[:x.last_valid_index()].ffill()))
    mid_price = mid_price.droplevel(0)
    return mid_price
