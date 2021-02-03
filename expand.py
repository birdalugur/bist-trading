import pandas as pd


def expands(data, td=pd.Timedelta(weeks=1)):
    first_df = data.first(td)

    current_date = first_df.index[-1].date()

    time_list = list(data.index[~data.index.isin(first_df.index)])

    first_index = first_df.index[0]

    __expands = [first_df]

    while time_list:
        current_index = time_list.pop(0)

        new_data = data.loc[current_index]

        if current_index.date() > current_date:
            current_date = current_index.date()
            first_index = current_index - td
            first_df = first_df[first_df.index > first_index]

        first_df = first_df.append(new_data)

        __expands.append(first_df)

    return __expands
