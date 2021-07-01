#!/usr/bin/env python
# coding: utf-8


import pandas as pd
from plotly.offline import plot
import plotly.graph_objects as go


path = "mid_freq_5Min_window_size_600_threshold_0.5_intercept_False_wavelet_False_ln_False_signalFunc_get_signal_reverse_False_tradeTable.csv"


time_cols = ["exit time", "entry time", "entry time div", "exit time div"]


data = pd.read_csv(path, parse_dates=time_cols)


data['time'] = data['exit time']-data['entry time']


data['time div'] = data['exit time div']-data['entry time div']


data['long'] = (data['exit_price_1'] - data['entry_price_1']) / \
    data['entry_price_1']
data['short'] = -(data['exit_price_2'] -
                  data['entry_price_2']) / data['exit_price_2']
data['return'] = data['long'] + data['short']


trade_minute = data['time'].astype('timedelta64[m]')


layout = dict(xaxis=dict(title='Time (Minute)',),
              yaxis=dict(title='Return'))


scat = go.Scatter(x=trade_minute, y=data['return'], mode='markers')


fig = go.Figure(data=scat, layout=layout)


file_name_1 = "scatter plot of returns"
_path = file_name_1 + '.html'
plot(fig, auto_open=False, filename=_path)


data['div_long'] = (data['div_exit_price_1'] -
                    data['div_entry_price_1']) / data['div_entry_price_1']
data['div_short'] = -(data['div_exit_price_2'] -
                      data['div_entry_price_2']) / data['div_exit_price_2']
data['div_return'] = data['div_long'] + data['div_short']


div_trade_minute = data['time'].astype('timedelta64[m]')


div_scat = go.Scatter(x=div_trade_minute, y=data['div_return'], mode='markers')


div_fig = go.Figure(data=div_scat, layout=layout)


file_name_2 = "scatter plot of div returns"
_path = file_name_2 + '.html'
plot(div_fig, auto_open=False, filename=_path)
