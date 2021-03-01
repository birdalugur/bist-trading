import plotly.graph_objects as go
import plotly.offline as offline


def plot_signals(residuals, std, signal_func=get_signal):
    x = signal_func(residuals, std)

    res = pd.concat([residuals.reset_index(drop=True), std.reset_index(drop=True), x.reset_index(drop=True)], axis=1)

    res.dropna(inplace=True)
    res.reset_index(inplace=True, drop=True)

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

    offline.plot(fig)


def plot_return(total_return):
    cum_return = total_return.cumsum()

    fig_return = go.Scatter(x=total_return.index, y=total_return.values, name='return', line_color='rgb(45,197,197)')
    fig_cum = go.Scatter(x=cum_return.index, y=cum_return.values, name='cumulative return',
                         line_color='rgb(54,181,212)')
    fig = go.Figure()
    fig.add_traces([fig_return, fig_cum])
    offline.plot(fig)
