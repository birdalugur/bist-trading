#!/usr/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd
from typing import Union
from itertools import combinations
import statsmodels.api as sm
import random
import plotly.express as px
from importlib import reload

import mydata
import wavelets
import residual
import selling
import rolling

from get_stats import get_stats

# ## Read data

folder_path = '/home/ugur/bistlmts/data/BIST_Eylul/'

data = mydata.read(folder_path)

data = mydata.mid_price(data, agg_time='5Min')

# ## Select a pair

pair_names = mydata.pair_names[0:2]

window_size = pd.Timedelta(minutes=30)

all_results = []

for pair_name in pair_names:

    pair = data.loc[:, pair_name]

    result_std = get_stats(pair, window_size, pair_name)

    all_results.append(result_std)

result = pd.concat(all_results)

result.to_csv('resultssss.csv')
