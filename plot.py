import plotly.graph_objects as go
import plotly.offline as offline

import pandas as pd


def plot_signals(residuals, std, signal_func, title=None):
    x = signal_func(residuals, std)

    res = pd.concat([residuals, std, x], axis=1)

    res.dropna(inplace=True)

    fig_res = go.Scatter(x=res.index, y=res.iloc[:, 0], name='residuals', line_color='rgb(45,197,197)')
    fig_std = go.Scatter(x=res.index, y=res.iloc[:, 1], name='std', line_color='rgb(248,195,184)')
    fig_std2 = go.Scatter(x=res.index, y=res.iloc[:, 1] * -1, name='-std', line_color='rgb(248,195,184)')

    fig_s1 = go.Scatter(x=res[res.signal1 == 1].index, y=res[res.signal1 == 1].iloc[:, 0], name='signal1',
                        mode='markers',
                        marker_color='rgb(236,81,18)')
    fig_s2 = go.Scatter(x=res[res.signal2 == 1].index, y=res[res.signal2 == 1].iloc[:, 0], name='signal2',
                        mode='markers',
                        marker_color='rgb(139,212,33)')

    fig = go.Figure()

    fig.add_traces([fig_res, fig_std, fig_std2, fig_s1, fig_s2])

    if title:
        lyt = go.Layout(title=go.layout.Title(text=title))
        fig.update_layout(lyt)

    offline.plot(fig, filename=title)


def plot_return(total_return, title=None):
    cum_return = total_return.cumsum()

    fig_return = go.Scatter(x=total_return.index, y=total_return.values, name='return', line_color='rgb(45,197,197)')
    fig_cum = go.Scatter(x=cum_return.index, y=cum_return.values, name='cumulative return',
                         line_color='rgb(54,181,212)')
    fig = go.Figure()
    fig.add_traces([fig_return, fig_cum])
    if title:
        lyt = go.Layout(title=go.layout.Title(text=title))
        fig.update_layout(lyt)
    offline.plot(fig, filename=title)


def plot_all_cumsum(path):
    data = pd.read_csv(path)

    # data['long'] = (data['exit_price_1'] - data['entry_price_1']) * 100
    # data['short'] = -(data['exit_price_2'] - data['entry_price_2']) * 100

    data['long'] = (data['exit_price_1'] - data['entry_price_1']) / data['entry_price_1']
    data['short'] = -(data['exit_price_2'] - data['entry_price_2']) / data['entry_price_2']

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

    offline.plot(fig, auto_open=False, filename=plot_name + '.html')
