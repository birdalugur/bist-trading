import pandas as pd
from itertools import combinations
import numpy as np

from trading_table import trading_table
import auxiliary as aux

import residual
import returns
import rolling
import signals
import plot

folder_path = 'data/data_202010.csv'

data = pd.read_csv(folder_path, parse_dates=['time'])
data = data[data.time.dt.hour < 15]
data['mid_price'] = (data['bid_price'] + data['ask_price']) / 2

pair_name = ('DOHOL', 'PETKM')

mid_freq = '10Min'
window_size = 300
threshold = 1
intercept = True
wavelet = False
ln = True
signal_func = signals.get_signal2
name = '_'.join(pair_name) + '_' + signal_func.__name__.split('_')[1]

pair_bid, pair_ask, pair_mid = aux.create_bid_ask_mid(pair_name, data)
pair_mid = pair_mid.groupby(pd.Grouper(freq='D')).resample(mid_freq).mean().droplevel(0)
pair_mid = pair_mid.resample('D').apply(aux.fill_nan).droplevel(0)

if ln:
    pair_mid = np.log(pair_mid)

pair_ask = pair_ask.resample('D').apply(aux.fill_nan).droplevel(0)

pair_bid = pair_bid.resample('D').apply(aux.fill_nan).droplevel(0)

pair_mid.dropna(inplace=True)
pair_ask.dropna(inplace=True)
pair_bid.dropna(inplace=True)

plot.plot_line(pair_mid, 'Mid Price.html')

all_windows = rolling.windows(pair_mid, window_size)
residuals = list(map(lambda w: residual.get_resid(w, intercept=intercept, wavelet=wavelet), all_windows))
std = [resid.std() for resid in residuals]
residuals = pd.concat(map(lambda r: r.tail(1), residuals))  # get last values
std = pd.Series(std, index=residuals.index)
residuals = residuals.dropna().reindex(pair_mid.index)
std = std.dropna().reindex(pair_mid.index) * threshold

plot.plot_signals(residuals, std, signal_func, name)

all_signals = signal_func(residuals, std)

return_values = returns.get_return(pair_ask, pair_bid, pair_mid, all_signals, 'rate', mid_freq)

plot.plot_return(return_values['return_value'], name)

trade_times = signals.trade_times(all_signals)

plot.plot_trades(return_values['return_value'], trade_times, 'Return Values - ' + name)
