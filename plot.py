import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import plot
import os

pio.renderers.default = "browser"
if 'graph' not in os.listdir():
    os.mkdir('graph')

if 'cumsum' not in os.listdir():
    os.mkdir('cumsum')


def trades(data, threshold, trades: list, name):
    fig = go.Figure()
    line_1 = go.Scatter(x=data.index, y=data, mode='lines', name='residuals')
    line_2 = go.Scatter(x=threshold.index, y=threshold, mode='lines', name='threshold')

    line_mirror = go.Scatter(x=threshold.index, y=-threshold, mode='lines', name='threshold_mirror', line_color='red')
    fig.add_traces([line_1, line_2, line_mirror])

    count = 0
    for trade in trades:
        count = count + 1
        sctr = go.Bar(x=trade.index, y=trade * 100, marker_color='black', name='trade_' + str(count))
        fig.add_trace(sctr)
    plot(fig, auto_open=False, filename='graph/' + '_'.join(name)+'.html')



def cumsum(cumsum, name, trades=None):
    fig = go.Figure()
    line_3 = go.Scatter(x=cumsum.index, y=cumsum, mode='lines', name='cumsum')
    fig.add_trace(line_3)

    if trades is not None:
        count = 0
        for trade in trades:
            count = count + 1
            sctr = go.Bar(x=trade.index, y=trade * 100, marker_color='black', name='trade_' + str(count))
            fig.add_trace(sctr)

    plot(fig, auto_open=False, filename='cumsum/' + '_'.join(name)+'.html')
