import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "browser"


def trades(data, threshold, trades: list):
    fig = go.Figure()
    line_1 = go.Scatter(x=data.index, y=data, mode='lines', name='residuals')
    line_2 = go.Scatter(x=threshold.index, y=threshold, mode='lines', name='threshold')
    line_mirror = go.Scatter(x=threshold.index, y=-threshold, mode='lines', name='threshold_mirror', line_color='red')
    fig.add_traces([line_1, line_2, line_mirror])

    count = 0
    for trade in trades:
        count = count + 1
        sctr = go.Bar(x=trade.index, y=trade * 10, marker_color='black', name='trade_' + str(count))
        fig.add_trace(sctr)
    fig.show()

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
