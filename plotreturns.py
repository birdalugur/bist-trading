"""
Graphs the cumulative return for each pair using the trade table.

Inputs:
    file_path (str):
    divergence (bool):
    only_positives (bool):
Output:
    line charts (html file)
"""

import pandas as pd
import plotly.express as px
import plotly.offline as offline

# read trade table file
file_path = "mid_freq_5Min_window_size_600_threshold_0.5_intercept_False_wavelet_False_ln_False_signalFunc_get_signal_reverse_False_tradeTable.csv"
divergence = True
only_positives = True

trade_table = pd.read_csv(file_path)

# calculate returns
if divergence:
    trade_table['long'] = (trade_table['div_exit_price_1'] - trade_table['div_entry_price_1']) / trade_table[
        'div_entry_price_1']
    trade_table['short'] = -(trade_table['div_exit_price_2'] - trade_table['div_entry_price_2']) / trade_table[
        'div_exit_price_2']
    trade_table['return'] = trade_table['long'] + trade_table['short']
else:
    trade_table['long'] = (trade_table['exit_price_1'] - trade_table['entry_price_1']) / trade_table['entry_price_1']
    trade_table['short'] = -(trade_table['exit_price_2'] - trade_table['entry_price_2']) / trade_table['exit_price_2']
    trade_table['return'] = trade_table['long'] + trade_table['short']

# each pair sorted by entry time
trade_table = trade_table.sort_values(["pair", "entry time"])

# calculating the cumulative return for each pair
trade_table["cum_return"] = trade_table.groupby("pair")["return"].cumsum()


def positive_trades(ttable):
    """
    Pozitif biten pair isimlerini döndürür."""
    last_values = ttable.groupby("pair")["cum_return"].last(1)
    return last_values[last_values > 0].index.values


if only_positives:
    positive_pairs = positive_trades(trade_table)
    trade_table = trade_table[trade_table.pair.isin(positive_pairs)].sort_values(["pair", "entry time"])
    pd.DataFrame({file_path: positive_pairs}).to_csv("divergence_" + str(divergence) + "positive_pairs.csv")

# plot graph and export html
file_name = "divergence_" + str(divergence) + "_only_positives_" + str(only_positives)
chart_title = file_path + "<br>" + str(len(positive_pairs)) + ' Cumulative returns - ' + 'divergence: ' + str(
    divergence) + ' only positives: ' + str(only_positives)
fig = px.line(trade_table, x="entry time", y="cum_return", color="pair")
fig.update_layout(title=chart_title)
offline.plot(fig, filename=file_name + ".html")
