import random
from typing import Union
from itertools import combinations

import numpy as np
import pandas as pd
import statsmodels.api as sm
import plotly.express as px

from rpy2 import robjects
from rpy2.robjects.packages import importr
# from rpy2.robjects.packages import PackageNotInstalledError

utils = importr('utils')

wavelets = importr('wavelets')

# try:
#     wavelets = importr('wavelets')
# except PackageNotInstalledError:
#     utils.install_packages('wavelets')
#     wavelets = importr('wavelets')


def convert_Rvectors(values):
    """
    Converts python array to r vector. If any, NaN values are removed.
    """
    values = values.dropna()
    vector = robjects.FloatVector(values)
    return vector


def mra_s1(data):
    """
    Return a list with element i comprised of a matrix containing the i'th level wavelet smooths.
    """
    params = {'n.levels': 1, 'filter': 'la8', "boundary": "periodic", "method": "modwt"}
    mra = wavelets.mra(convert_Rvectors(data), **params)
    s_data = mra.slots['S']
    s_data = dict(zip(s_data.names, map(list, list(s_data))))
    result = pd.Series(s_data['S1'])
    return result
