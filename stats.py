import pandas as pd

data = pd.read_csv("bs_ARCLK_BIMAS.csv", parse_dates=['exit_time', 'entry_time'])


pairs = pd.concat([data.entry_symbol_1, data.entry_symbol_2], axis=1)
pairs = pairs.apply(lambda x: sorted(x), axis=1)
pairs = pairs.apply(lambda x: '_'.join(x))


data['pair'] = pairs


data['long'] = (data['exit_price_1'] - data['entry_price_1']) * 100
data['short'] = -(data['exit_price_2'] - data['entry_price_2']) * 100

data['return'] = data['long'] + data['short']


data['return_median'] = data['return'].median()


c_long = data.groupby('pair')['long'].cumsum()
c_short = data.groupby('pair')['short'].cumsum()
data['c_return'] = c_long + c_short


last_c_return = data.groupby('pair')['c_return'].apply(lambda x: x.iloc[-1])


number_of_trades = data.groupby('pair').size()


c_return_per_trade = last_c_return / number_of_trades


c_return_per_trade.name = 'c_return_per_trade'


data = data.merge(c_return_per_trade, left_on='pair', right_index=True)


data['duration'] = data['exit_time'] - data['entry_time']

duration_trades_median = data.groupby('pair').apply(lambda x: x['duration'].median())

duration_trades_median.name = 'duration_trades_median'


data = data.merge(duration_trades_median, left_on='pair', right_index=True)


first_result = data.copy()




data = data.sort_values('c_return', ascending=False)

average = data.mean()

num_positive = data[data.c_return > 0].count()

avg_positive = data[data.c_return > 0].mean()

avg_20 = data.head(20).mean()

result = pd.DataFrame([average, avg_positive, avg_20, num_positive],
                      index=['avg', 'positive_avg', 'first_20_avg', 'return_positive'])





# import pandas as pd
#
# data = pd.read_csv('../rol300_noint_5min_thr1_std.csv')
#
# data.duration_trades_median = pd.to_timedelta(data.duration_trades_median)
# data.duration_trades_mean = pd.to_timedelta(data.duration_trades_mean)
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
