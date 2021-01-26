import numpy as np
import pandas as pd
from typing import Union
from itertools import combinations
import statsmodels.api as sm
import random
import plotly.express as px
from wavelets import mra_s1


def residuals(first, second, intercept=False):
    first_symbol = first.values.reshape(-1, 1)
    second_symbol = second.values.reshape(-1, 1)
    if intercept:
        first_symbol = sm.add_constant(first)
    model = sm.OLS(second_symbol, first_symbol).fit()
    resid = pd.Series(model.resid)
    return resid


def get_resid(pair, intercept=False, w_la8_1=False):
    first = pair.iloc[:, 0]
    second = pair.iloc[:, 1]

    idx = pair.index

    name = '_'.join((first.name, second.name))

    if w_la8_1:
        first = mra_s1(first)
        second = mra_s1(second)

    resids = residuals(first, second, intercept)
    resids.name = name
    resids.index = idx

    return resids


def rollPair(pair, window, intercept=False, w_la8_1=False):
    start = 0
    lenght = len(pair) - window + 1
    end = window
    name = '_'.join(pair.columns)
    all_idx = []
    all_values = []

    for i in range(window - 1):
        all_values.append(None)
        all_idx.append(pair.index[i])

    for i in range(lenght):
        item = pair[start:end]
        idx = item.index[-1]
        value = get_resid(item, intercept, w_la8_1).tail(1).values[0]

        start = start + 1
        end = end + 1

        all_idx.append(idx)
        all_values.append(value)

    return pd.Series(all_values, index=all_idx, name=name)

