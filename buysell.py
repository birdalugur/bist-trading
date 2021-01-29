import pandas as pd
# name_long = pair_name[0]
# name_short = pair_name[1]
#
# signal_type = 's2'
#
# entry_points = entry_points_s2
# exit_points = exit_points_s2


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