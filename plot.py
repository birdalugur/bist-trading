import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import plot
import os

pio.renderers.default = "browser"
if 'graph' not in os.listdir():
    os.mkdir('graph')


def trades(data, threshold, trades: list, name, creturn):
    fig = go.Figure()
    line_1 = go.Scatter(x=data.index, y=data, mode='lines', name='residuals')
    line_2 = go.Scatter(x=threshold.index, y=threshold, mode='lines', name='threshold')
    line_3 = go.Scatter(x=creturn.index, y=creturn, mode='lines', name='cumsum')
    line_mirror = go.Scatter(x=threshold.index, y=-threshold, mode='lines', name='threshold_mirror', line_color='red')
    fig.add_traces([line_1, line_2, line_mirror, line_3])

    count = 0
    for trade in trades:
        count = count + 1
        sctr = go.Bar(x=trade.index, y=trade * 10, marker_color='black', name='trade_' + str(count))
        fig.add_trace(sctr)
    plot(fig, auto_open=False, filename= 'graph/' + '_'.join(name)+'.html')


#
# import plotly.graph_objects as go
#
#
# fig = go.Figure(data=[go.Bar(
#     x=x.index,
#     y=x.values,
#     width=[0.8, 0.8, 0.8, 3.5, 4] # customize width here
# )])
#
# fig.show()
#
#
# fig.add_trace(go.Bar(
#     x=x.index,
#     y=x.values,
#     marker_color='black'
#     # customize width here
# ))
