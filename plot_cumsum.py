import plotly.graph_objects as go
from plotly.offline import plot
import pandas as pd

path = 'mid_freq_5Min_window_size_300_threshold_1_intercept_False_wavelet_False_tradeTable.csv'

data = pd.read_csv(path)

data['long'] = (data['exit_price_1'] - data['entry_price_1']) * 100
data['short'] = -(data['exit_price_2'] - data['entry_price_2']) * 100
data['return'] = data['long'] + data['short']

data = data.sort_values(['pair', 'exit time'])

# Cumulative return hesapla
c_long = data.groupby('pair')['long'].cumsum()
c_short = data.groupby('pair')['short'].cumsum()
data['c_return'] = c_long + c_short

c_return = data[['pair', 'exit time', 'c_return']]

pairs = c_return['pair'].unique()

lines = []

for pair in pairs:
    pair_data = c_return[c_return['pair'] == pair]
    pair_data = pair_data.sort_values('exit time')
    line = go.Scatter(x=pair_data['exit time'], y=pair_data['c_return'], mode='lines', name=pair)
    lines.append(line)

fig = go.Figure()

fig.add_traces(lines)

plot_name = path.split('.')[0]

plot(fig, auto_open=False, filename=plot_name+'.html')
