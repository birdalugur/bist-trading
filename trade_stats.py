import pandas as pd

path = "tt.csv"

data = pd.read_csv(path, parse_dates=['exit time', 'entry time'])


# Pairları oluştur
pairs = pd.concat([data.entry_symbol_1, data.entry_symbol_2], axis=1)
pairs = pairs.apply(lambda x: sorted(x), axis=1)
pairs = pairs.apply(lambda x: '_'.join(x))
data['pair'] = pairs

# Return hesapla
data['long'] = (data['exit_price_1'] - data['entry_price_1']) * 100
data['short'] = -(data['exit_price_2'] - data['entry_price_2']) * 100
data['return'] = data['long'] + data['short']

# Cumulative return hesapla
c_long = data.groupby('pair')['long'].cumsum()
c_short = data.groupby('pair')['short'].cumsum()
data['c_return'] = c_long + c_short

# Her bir trade için süreler
data['duration'] = data['exit time'] - data['entry time']

# Her pair için trade sayısı
number_of_trades = data.groupby('pair').size()

# Her pair için returnun medianı
return_median = data.groupby('pair')['return'].median()

# Her pair için cumulative returnun son değeri
last_c_return = data.groupby('pair')['c_return'].apply(lambda x: x.iloc[-1])

duration_median = data.groupby('pair').apply(lambda x: x['duration'].median())

mean_lastc_return = last_c_return / number_of_trades

stats_data = pd.concat([last_c_return, number_of_trades, mean_lastc_return, duration_median, return_median], axis=1)
columns = ['last_c_return', 'number_of_trade', 'mean_lastc_return', 'duration_median', 'return_median']
stats_data.columns = columns


stats_data.to_csv('stats_'+path)


data = stats_data.sort_values('last_c_return', ascending=False)

average = data.mean()

num_positive = data[data.last_c_return > 0].count()

avg_positive = data[data.last_c_return > 0].mean()

avg_20 = data.head(20).mean()

result = pd.DataFrame([average, avg_positive, avg_20, num_positive],
                      index=['avg', 'positive_avg', 'first_20_avg', 'return_positive'])
