import pandas as pd

import mydata
import residual
import selling
import rolling


def get_first_prices(ts, points):
    """Verilen zamana ait ilk işlemi döndürür. İşlem yoksa NaN kabul edilir."""

    new_ts = pd.Series()
    ts = ts.dropna()

    for point in points:
        # t = point.strftime('%Y-%m-%d %H:%M')
        t = str(point)
        x = ts[t]

        if len(x) == 0:
            be_added = pd.Series(data=None, index=[point])
        else:
            be_added = x.head(1)
        new_ts = new_ts.append(be_added)
    new_ts.name = ts.name

    return new_ts


def trading_table(pair_mid, pair_ask, pair_bid, window_size, threshold, intercept, wavelet):
    # calculate residuals & std from windows >>>>>>>>>>>>>>>>>>>>>>>>>>
    all_windows = rolling.windows(pair_mid, window_size)
    residuals = list(map(lambda w: residual.get_resid(w, intercept=intercept, wavelet=wavelet), all_windows))
    std = [resid.std() for resid in residuals]
    residuals = pd.concat(map(lambda r: r.tail(1), residuals))  # get last values
    std = pd.Series(std, index=residuals.index)
    residuals = residuals.dropna().reindex(pair_mid.index)
    std = std.dropna().reindex(pair_mid.index) * threshold
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Find signals >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    signal_1, signal_2 = selling.get_signal(residuals, std)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Mark entry - exit points >>>>>>>>>>>>>>>>>>>>>>>>>
    entry_points_s1, exit_points_s1 = selling.signal_points(signal_1)
    entry_points_s2, exit_points_s2 = selling.signal_points(signal_2)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Signal 1'den gelen pointslerden pair_0 short yani -> Sell
    # Signal 1'den gelen pointslerden pair_1 long yani -> Buy

    # Signal 2'den gelen pointslerden pair_0 long yani -> Buy
    # Signal 2'den gelen pointslerden pair_1 short yani -> Sell

    # S'ler price 2 ' ye
    # B'ler price 1 ' e

    # ask price -> alım fiyatı
    # bid price -> satış fiyatı

    entry_price_buy_1 = get_first_prices(pair_ask.iloc[:, 1], entry_points_s1)
    entry_price_buy_2 = get_first_prices(pair_ask.iloc[:, 0], entry_points_s2)

    exit_price_buy_1 = get_first_prices(pair_ask.iloc[:, 1], exit_points_s1)
    exit_price_buy_2 = get_first_prices(pair_ask.iloc[:, 0], exit_points_s2)

    entry_price_sell_1 = get_first_prices(pair_bid.iloc[:, 0], entry_points_s1)
    entry_price_sell_2 = get_first_prices(pair_bid.iloc[:, 1], entry_points_s2)

    exit_price_sell_1 = get_first_prices(pair_bid.iloc[:, 0], exit_points_s1)
    exit_price_sell_2 = get_first_prices(pair_bid.iloc[:, 1], exit_points_s2)


    buy1_entry = pd.DataFrame({'entry_price_1': entry_price_buy_1, 'entry_symbol_1': entry_price_buy_1.name})
    buy2_entry = pd.DataFrame({'entry_price_1': entry_price_buy_2, 'entry_symbol_1': entry_price_buy_2.name})

    sell1_entry = pd.DataFrame({'entry_price_2': entry_price_sell_1, 'entry_symbol_2': entry_price_sell_1.name})
    sell2_entry = pd.DataFrame({'entry_price_2': entry_price_sell_2, 'entry_symbol_2': entry_price_sell_2.name})

    buy1_exit = pd.DataFrame({'exit_price_1': exit_price_buy_1, 'exit_symbol_1': exit_price_buy_1.name})
    buy2_exit = pd.DataFrame({'exit_price_1': exit_price_buy_2, 'exit_symbol_1': exit_price_buy_2.name})

    sell1_exit = pd.DataFrame({'exit_price_2': exit_price_sell_1, 'exit_symbol_2': exit_price_sell_1.name})
    sell2_exit = pd.DataFrame({'exit_price_2': exit_price_sell_2, 'exit_symbol_2': exit_price_sell_2.name})

    buy_entry = buy1_entry.append(buy2_entry).assign(entry_side_1='B')
    sell_entry = sell1_entry.append(sell2_entry).assign(entry_side_2='S')
    buy_exit = buy1_exit.append(buy2_exit).assign(exit_side_1='B')
    sell_exit = sell1_exit.append(sell2_exit).assign(exit_side_2='S')

    entry_data = buy_entry.merge(sell_entry, left_index=True, right_index=True, how='outer')
    entry_data.index.name = 'entry time'

    exit_data = buy_exit.merge(sell_exit, left_index=True, right_index=True, how='outer')
    exit_data.index.name = 'exit time'

    result = pd.concat([entry_data.reset_index(), exit_data.reset_index()], axis=1)

    # Pairları oluştur
    pairs = pd.concat([result.entry_symbol_1, result.entry_symbol_2], axis=1)
    pairs = pairs.apply(lambda x: sorted(x), axis=1)
    pairs = pairs.apply(lambda x: '_'.join(x))
    result['pair'] = pairs

    return result

