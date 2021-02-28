from typing import Union
import pandas as pd


def find_frequency(times: pd.DatetimeIndex) -> pd.Timedelta:
    """Verilen zaman serisinin frekansını döndürür."""
    ts = pd.Series(times)
    freq = ts.diff()[1]
    return freq


def get_window_period(times: pd.DatetimeIndex, window: Union[pd.Timedelta, int]) -> int:
    """
    Gün geçişlerinde, periodlardaki eksilmeyi önlemek için,
    Zaman nesnesi olarak verilen window değerine karşılık gelen
     int değerini döndürür.
    """

    if type(window) == int:
        return window
    freq = find_frequency(times)
    return int(window / freq)


def windows(data, window: Union[int, pd.Timedelta]) -> list:
    """Return moving windows"""
    window_value = get_window_period(data.index, window)
    windows = data.rolling(window_value)
    return list(windows)[window_value - 1:]


def std(values, window_size):
    std_window = windows(values, window_size)
    idx = map(lambda x: x.index[-1], std_window)
    std_values = map(lambda x: x.std(), std_window)

    return pd.Series(std_values, index=idx, name='std')
