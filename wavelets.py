from rpy2 import robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.packages import PackageNotInstalledError
utils = importr('utils')

import numpy as np
import pandas as pd

from typing import Union
from itertools import combinations

import statsmodels.api as sm
import random
import plotly.express as px

from residual import get_resid


try:
    wavelets = importr('wavelets')
except PackageNotInstalledError:
    utils.install_packages('wavelets')
    wavelets = importr('wavelets')
    
    
    
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
    params = {'n.levels': 1,'filter':'la8', "boundary":"periodic", "method":"modwt"}
    mra=wavelets.mra(convert_Rvectors(data),**params)
    s_data=mra.slots['S']
    s_data = dict(zip(s_data.names, map(list,list(s_data))))
    return s_data['S1']



def roll_mra(pair, window):

    idx = pair.index

    first = pair.iloc[:,0]

    second = pair.iloc[:,1] 

    first = first.rolling(window).apply(lambda x: mra_s1(x)[-1])

    second = second.rolling(window).apply(lambda x: mra_s1(x)[-1])

    idx_nonan = first.dropna().index

    resids = residuals(first.dropna(),second.dropna())

    resids.index = idx_nonan

    resids = resids.reindex(idx)

    return resids


def residuals(first, second):
    first_symbol = first.values.reshape(-1, 1)
    second_symbol = second.values.reshape(-1, 1)
    model = sm.OLS(second_symbol, first_symbol).fit()
    resid = pd.Series(model.resid)
    return resid
