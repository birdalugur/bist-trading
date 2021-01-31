import pandas as pd

data = pd.read_csv("bs_rol300_noint_5min_thr1_std.csv", parse_dates=['exit_time', 'entry_time'])

long = (data['exit_price_1'] - data['entry_price_1']) * 100
short = -(data['exit_price_2'] - data['entry_price_2']) * 100

c_long = long.cumsum()
c_short = short.cumsum()
c_returns = c_long + c_short

returns = long + short

data['long'] = long
data['short'] = short
data['c_long'] = c_long
data['c_short'] = c_short
data['c_return'] = c_returns
data['return'] = returns

last_c_return = data.set_index(['entry_symbol_1', 'entry_symbol_2']).groupby(level=[0, 1])['c_return'].tail(1)
number_of_trades = data.groupby(['entry_symbol_1', 'entry_symbol_2']).size()

c_return_per_trade = last_c_return / number_of_trades
c_return_per_trade.name = 'c_return_per_trade'
data = data.merge(c_return_per_trade, left_on=['entry_symbol_1', 'entry_symbol_2'], right_index=True)

data.drop('Unnamed: 0', inplace=True, axis=1)

data['duration'] = data['exit_time'] - data['entry_time']

data = data[
    ['long', 'short', 'c_long', 'c_short', 'return', 'duration', 'last_return', 'c_return', 'c_return_per_trade']]

data = data.sort_values('c_return', ascending=False)

average = data.mean()

num_positive = data[data.c_return > 0].count()

avg_positive = data[data.c_return > 0].mean()

avg_20 = data.head(20).mean()

result = pd.DataFrame([average, avg_positive, avg_20, num_positive],
                      index=['avg', 'positive_avg', 'first_20_avg', 'return_positive'])

# duration_trades_median = data.groupby(['entry_symbol_1', 'entry_symbol_2']).apply(
#     lambda x: x['duration'].median())
#
# duration_trades_mean = data.groupby(['entry_symbol_1', 'entry_symbol_2']).apply(
#     lambda x: x['duration'].mean())
#
#
# number_trades = data.groupby(['entry_symbol_1', 'entry_symbol_2']).size()
#
#
# data = data.sort_values('c_return', ascending=False)
#
#
#
#
# average = data.mean()
#
# num_positive = data[data.c_return > 0].count()
#
# avg_positive = data[data.c_return > 0].mean()
#
# avg_20 = data.head(20).mean()
#
# result = pd.DataFrame([average, avg_positive, avg_20, num_positive], index=['avg', 'positive', 'avg_20', 'num'])
#
#
#
#
#

# import pandas as pd
#
# data = pd.read_csv('../rol300_noint_5min_thr1_std.csv')
#
# data.duration_trades_median = pd.to_timedelta(data.duration_trades_median)
# data.duration_trades_mean = pd.to_timedelta(data.duration_trades_mean)
#
#
#
# data = data.sort_values('c_return', ascending=False)
#
# average = data.mean()
#
# num_positive = data[data.c_return > 0].count()
#
# avg_positive = data[data.c_return > 0].mean()
#
# avg_20 = data.head(20).mean()
#
# result = pd.DataFrame([average, avg_positive, avg_20, num_positive], index=['avg', 'positive', 'avg_20', 'num'])
#
#
#
