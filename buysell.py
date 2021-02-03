import pandas as pd

import mydata
import residual
import selling
import rolling

data = pd.read_csv('data.csv', parse_dates=['time'], index_col=['time'])

# Options >>>>>>>>>>>>>>>>>>>>>>>>
window_size = 300
threshold = 1
stats_type = 'standart'
intercept = False
w_la8_1 = False
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# Select a pair >>>>>>>>>>>>>>>>>>>
pair_name = mydata.pair_names[1]
pair = data.loc[:, pair_name]
pair.dropna(inplace=True)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# calculate residuals & std from windows >>>>>>>>>>>>>>>>>>>>>>>>>>
all_windows = rolling.windows(pair, window_size)
residuals = list(map(lambda w: residual.get_resid(w, intercept=intercept, w_la8_1=w_la8_1), all_windows))
std = [resid.std() for resid in residuals]
residuals = pd.concat(map(lambda r: r.tail(1), residuals))  # get last values
std = pd.Series(std, index=residuals.index)
residuals = residuals.dropna().reindex(pair.index)
std = std.dropna().reindex(pair.index) * threshold
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# Find signals >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
signal_1, signal_2 = selling.get_signal(residuals, std)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# Mark entry - exit points >>>>>>>>>>>>>>>>>>>>>>>>>
entry_points_s1, exit_points_s1 = selling.signal_points(signal_1)
entry_points_s2, exit_points_s2 = selling.signal_points(signal_2)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<



def buy_sell_stats(pair, name_long, name_short, entry_points, exit_points, signal_type):
    df_entry = pair.loc[entry_points]
    df_exit = pair.loc[exit_points]

    if signal_type == 's2':
        df_entry.columns = ['entry_price_1', 'entry_price_2']
        df_exit.columns = ['exit_price_1', 'exit_price_2']
    if signal_type == 's1':
        df_entry.columns = ['entry_price_2', 'entry_price_1']
        df_exit.columns = ['exit_price_2', 'exit_price_1']

    df_entry['entry_symbol_1'] = name_long
    df_entry['entry_symbol_2'] = name_short

    df_entry['entry_side_1'] = 'B'
    df_entry['entry_side_2'] = 'S'

    df_entry.index.name = 'entry_time'

    df_exit['exit_symbol_1'] = name_long
    df_exit['exit_symbol_2'] = name_short
    df_exit['exit_side_1'] = 'B'
    df_exit['exit_side_2'] = 'S'

    df_exit.index.name = 'exit_time'

    df = pd.concat([
        df_entry.reset_index(),
        df_exit.reset_index()
    ], axis=1)

    df['signal_type'] = signal_type

    cols = ['entry_symbol_1', 'entry_time', 'entry_price_1', 'entry_side_1',
            'entry_symbol_2', 'entry_price_2', 'entry_side_2',
            'exit_symbol_1', 'exit_time', 'exit_price_1', 'exit_side_1',
            'exit_symbol_2', 'exit_price_2', 'exit_side_2', 'signal_type'
            ]

    df = df[cols]

    return df



s1 = buy_sell_stats(pair, name_long=pair_name[1], name_short=pair_name[0], entry_points=entry_points_s1,
                    exit_points=exit_points_s1, signal_type='s1')



s2 = buy_sell_stats(pair, name_long=pair_name[0], name_short=pair_name[1], entry_points=entry_points_s2,
                    exit_points=exit_points_s2, signal_type='s2')


buy_sell = pd.concat([s2, s1])


buy_sell.to_csv('bs_'+'_'.join(pair_name)+'.csv', index=False)