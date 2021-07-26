import pandas as pd
import numpy as np


def get_signal(residuals: pd.Series, thresholds: pd.Series, coeff_negative: int, coeff_positive: int) -> pd.DataFrame:
    """
    Residual, standart sapmayı geçince sinyal aç. İşaret ++ ise signal_1=True, -- ise signal_2=True.
    Resid > std ve işaret değişimi yoksa mevcut sinyallerin durumunu koru.
    Önceki işleme göre işaret değişirse ve resid < std ise her iki sinyal kapatılır.
    Önceki işleme göre işaret değişirse ve resid > std ise her bir sinyal kapatılırken diğeri açılır.
    """
    signal_1, signal_2 = [], []

    signal1, signal2 = False, False

    prev_sign = 0

    nan_lock = 1

    idx = residuals.index

    thresholds_positive = thresholds * coeff_negative

    thresholds_negative = thresholds * coeff_positive

    for i in range(len(residuals)):
        residual = residuals.iloc[i]
        sign = np.sign(residual)
        if sign == 1:
            thresholds = thresholds_positive
        else:
            thresholds = thresholds_negative
        threshold = thresholds.iloc[i]

        if abs(residual) > threshold:
            nan_lock = 0
            prev_sign = sign
            if sign == 1:
                signal1 = True
                signal2 = False
            else:
                signal1 = False
                signal2 = True
        else:
            if sign == prev_sign:
                pass
            else:
                prev_sign = sign
                signal1 = False
                signal2 = False
            if nan_lock == 1:
                signal1 = np.nan
                signal2 = np.nan
        signal_1.append(signal1)
        signal_2.append(signal2)

    signal_1 = pd.Series(signal_1, index=idx, name='signal_1').replace({False: 0, True: 1})
    signal_2 = pd.Series(signal_2, index=idx, name='signal_2').replace({False: 0, True: 1})

    signal1, signal2 = signal_1.shift(), signal_2.shift()

    result = pd.DataFrame({'signal1': signal1, 'signal2': signal2})

    return result


def get_signal2(residuals, std, coeff: int):
    # TODO: must be edited according to the threshold coefficients.
    list_signal1, list_signal2 = [], []

    idx = residuals.index

    std = std * coeff

    number_of_nans = residuals.isna().value_counts()[True]

    for i in range(number_of_nans):
        list_signal1.append(np.nan)
        list_signal2.append(np.nan)

    is_prev_above_std = False
    prev_sign = np.sign(residuals[number_of_nans])

    signal1, signal2 = 0, 0

    if residuals[number_of_nans] > std[number_of_nans]:
        is_prev_above_std = True

    list_signal1.append(signal1)
    list_signal2.append(signal2)

    for _res, _std in zip(residuals[number_of_nans + 1:], std[number_of_nans + 1:]):

        current_sign = np.sign(_res)

        if current_sign == prev_sign:
            if (abs(_res) < _std) and is_prev_above_std:
                if current_sign == 1:
                    signal1 = 1
                    signal2 = 0
                else:
                    signal1 = 0
                    signal2 = 1
        else:
            signal1 = 0
            signal2 = 0
            prev_sign = current_sign

        if abs(_res) > _std:
            is_prev_above_std = True
        else:
            is_prev_above_std = False

        list_signal1.append(signal1)
        list_signal2.append(signal2)

    return pd.DataFrame({'signal1': list_signal1, 'signal2': list_signal2}, index=idx)


def signal_points(signal: pd.Series) -> [pd.Index, pd.Index]:
    """
    Returns the entry and exit_points points of the signal. -> (entry,exit_points)
    """
    entry_exit_points = np.trim_zeros(signal.dropna(), 'f').diff().fillna(1)
    entry_points = entry_exit_points[entry_exit_points == 1].index
    exit_points_points = entry_exit_points[entry_exit_points == -1].index
    if len(entry_points) > len(exit_points_points):
        entry_points = entry_points[0:len(exit_points_points)]
        # exit_points_points = exit_points_points.append(pd.DatetimeIndex([signal.index[-1]]))
    return entry_points, exit_points_points


def trade_times(all_signals):
    """
    Get the entry and exit time of each trade
    """
    signal_1, signal_2 = all_signals['signal1'], all_signals['signal2']

    # Mark entry - exit points >>>>>>>>>>>>>>>>>>>>>>>>>
    entry_points_s1, exit_points_s1 = signal_points(signal_1)
    entry_points_s2, exit_points_s2 = signal_points(signal_2)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    entry = entry_points_s1.append(entry_points_s2)
    exit = exit_points_s1.append(exit_points_s2)

    return pd.DataFrame({'entry_time': entry, 'exit_time': exit})
