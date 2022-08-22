import glob
import pandas as pd
import sys
import os

folder_path = 'trade_tables/'


def trade_stats(path):

    data = pd.read_csv(path, parse_dates=['exit time', 'entry time'])

    # data['long'] = (data['exit_price_1'] - data['entry_price_1']) * 100
    # data['short'] = -(data['exit_price_2'] - data['entry_price_2']) * 100
    # data['return'] = data['long'] + data['short']

    data['long'] = (data['exit_price_1'] -
                    data['entry_price_1']) / data['entry_price_1']
    data['short'] = -(data['exit_price_2'] -
                      data['entry_price_2']) / data['entry_price_2']
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
    c_return = data.groupby('pair')['c_return'].apply(lambda x: x.iloc[-1])

    # Her pair için cumulative returnun max değeri
    # max_c_return = data.groupby('pair')['c_return'].max()

    # Median Duration for all pairs
    duration_median = data.groupby('pair').apply(
        lambda x: x['duration'].median())

    # mean_c_return = c_return / number_of_trades

    stats_data = pd.concat(
        [c_return, number_of_trades, return_median, duration_median], axis=1)
    columns = ['c_return', 'number_of_trades',
               'return_median', 'duration_median']
    stats_data.columns = columns

    # stats_data.to_csv('stats_' + path)

    data = stats_data.sort_values('c_return', ascending=False)

    average = data.mean()

    num_positive = data[c_return > 0].count()

    avg_positive = data[data.c_return > 0].mean()

    avg_20 = data.head(20).mean()

    number_of_pairs = data.count()

    summary = pd.DataFrame([number_of_pairs, num_positive, avg_20, avg_positive, average],
                           index=['Number of Pairs', 'Number of Positive Pairs', 'Avg C_Return_Top20',
                                  'Avg C_Return_Positive', 'Avg C_Return'])

    summary = summary.unstack().reset_index()

    cols = summary['level_0'] + '_' + summary['level_1']

    vals = summary[0].values.reshape(1, -1)

    summary = pd.DataFrame(vals, columns=cols)

    return summary


all_paths = glob.glob(folder_path+'*.csv')

all_df = []
for path in all_paths:
    # name = path.split('/')[1].split('.')[0]
    df = trade_stats(path)
    df['file'] = path
    all_df.append(df)

result = pd.concat(all_df)
result = result.sort_values(['file', 'c_return_Avg C_Return'], ascending=False)

result = result[['c_return_Avg C_Return_Top20', 'c_return_Avg C_Return_Positive',
                 'c_return_Avg C_Return',
                 'c_return_Number of Pairs', 'c_return_Number of Positive Pairs',
                 'number_of_trades_Number of Pairs',
                 'number_of_trades_Number of Positive Pairs',
                 'number_of_trades_Avg C_Return_Top20',
                 'number_of_trades_Avg C_Return_Positive',
                 'number_of_trades_Avg C_Return', 'return_median_Number of Pairs',
                 'return_median_Number of Positive Pairs',
                 'return_median_Avg C_Return_Top20',
                 'return_median_Avg C_Return_Positive', 'return_median_Avg C_Return',
                 'duration_median_Number of Pairs',
                 'duration_median_Number of Positive Pairs',
                 'duration_median_Avg C_Return_Top20',
                 'duration_median_Avg C_Return_Positive', 'duration_median_Avg C_Return',
                 'file']]

result.to_csv(folder_path + 'all_trade_stats.csv', index=False)
