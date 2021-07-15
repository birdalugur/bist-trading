"""
This module contains functions defined in the R's LongMemoryTS package.
For documentation, use the docs() function.
"""

from math import floor

import pandas as pd
from rpy2 import robjects
from rpy2.robjects.packages import importr

# Create lmts object
lmts = importr('LongMemoryTS')


def isnull(values) -> bool:
    """
    Check empty data
    """
    if isinstance(values, pd.Series) and values.dropna().size == 0:
        return True


def docs():
    """
    Open the LongMemoryTS package documentation page.
    """
    import webbrowser
    webbrowser.open('https://www.rdocumentation.org/packages/LongMemoryTS/versions/0.1.0')


def convert_Rvectors(values):
    """
    Converts python array to r vector. If any, NaN values are removed.
    """
    values = values.dropna()
    vector = robjects.FloatVector(values)
    return vector


# >>>>>> estimation functions >>>>>>>>>


def elw(values, mean_est="mean"):
    """
    parameters can be changed as specified in the documentation
    """
    if isnull(values):
        return None
    vector = convert_Rvectors(values)
    _elw = lmts.ELW(vector, **{'m': floor(1 + len(vector) ** 0.6), 'mean.est': mean_est})[0][0]
    return _elw


def elw2s(values, trend_order=1, taper='HC'):
    """
    Two-Step Exact local Whittle estimator of fractional integration with unknown mean and time trend.
    """
    # TODO: @taper parametresi 'Velasco' olarak atandığında hata alınır.

    if isnull(values):
        return None

    vector = convert_Rvectors(values)

    try:
        _elw2s = \
            lmts.ELW2S(vector, **{'m': floor(1 + len(vector) ** 0.6), 'trend_order': trend_order, 'taper': taper})[0][0]
    except:
        raise Exception('Error for ', values.name)
    return _elw2s


def gph(values, l_value=1):
    if isnull(values):
        return None
    vector = convert_Rvectors(values)
    _gph = lmts.gph(vector, **{'m': floor(1 + len(vector) ** 0.6), 'l': l_value})[0]
    return _gph


def hou_perron(values):
    if isnull(values):
        return None
    vector = convert_Rvectors(values)
    _hou_perron = lmts.Hou_Perron(vector, **{'m': floor(1 + len(vector) ** 0.6)})[0][0]
    return _hou_perron


def local_w(values):
    if isnull(values):
        return None
    # TODO: @taper parametresi 'Velasco' olarak atandığında hata alınır.
    vector = convert_Rvectors(values)
    _local_w = lmts.local_W(vector,
                            **{'int': robjects.FloatVector([-0.5, 2.5]), 'm': floor(1 + len(vector) ** 0.6),
                               'diff_param': 1,
                               'taper': 'HC', 'l': 1})[0][0]
    return _local_w

# <<<<<< estimation functions <<<<<<<<<
