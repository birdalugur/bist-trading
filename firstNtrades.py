import pandas as pd
import glob

all_paths = list(glob.iglob('top20/*.csv', recursive=True))

data = pd.concat([pd.read_csv(path, parse_dates=['entry time', 'exit time']) for path in all_paths])


data['long'] = (data['exit_price_1'] - data['entry_price_1']) / data['entry_price_1']
data['short'] = -(data['exit_price_2'] - data['entry_price_2']) / data['entry_price_2']
data['return'] = data['long'] + data['short']


def first_n(x):
    _sorted = x.sort_values(['return', 'pair'], ascending=False)
    return pd.Series(_sorted.pair.unique()[0:20])


data['date'] = data['exit time'].dt.to_period('M')

pair_table = data.groupby('date').apply(first_n).T

pair_table = pair_table.shift(axis=1).bfill(axis=1)

data = data.set_index('exit time')

all_20 = []

for i in range(pair_table.shape[1]):
    pairs_by_date = pair_table.iloc[:, i]
    _date = str(pairs_by_date.name)
    _data = data.loc[_date]
    _first20data = _data[_data.pair.isin(pairs_by_date)]
    _first20data = _first20data.sort_values(['return', 'pair'], ascending=False)
    all_20.append(_first20data[['pair', 'return']])

first_20 = pd.concat(all_20).reset_index()

all_stats = first_20.groupby(['pair']).describe()

first_20['date'] = first_20['exit time'].dt.to_period('M')

monthly_mean = first_20.groupby(['date', 'pair']).mean()

monthly = monthly_mean.groupby(level=0).mean()

first_20 = first_20.sort_values(['date', 'return'], ascending=False).drop('date', axis=1)

all_stats.to_csv('all_stats.csv')
monthly_mean.to_csv('monthly_pair_mean.csv')
