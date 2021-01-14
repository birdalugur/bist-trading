import numpy as np
import pandas as pd
from typing import Union
from itertools import combinations
import statsmodels.api as sm
import random
import plotly.express as px


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


BIST30 = ["ARCLK", "ASELS", "BIMAS", "DOHOL", "EKGYO", "FROTO", "HALKB", "GARAN", "ISCTR", "KCHOL", "KOZAA", "KOZAL",
          "KRDMD", "AKBNK", "PETKM", "PGSUS", "SAHOL", "EREGL", "SODA", "TAVHL", "TCELL", "THYAO", "TKFEN",
          "TOASO", "TSKB", "TTKOM", "TUPRS", "VAKBN", "YKBNK"]
# SISE

pair_names = list(combinations(BIST30,2))


