import glob
import pandas as pd
import multiprocessing
import time

folder_path = '//10.1.1.10/shared/tob_changes_bist/'

BIST30 = ["ARCLK", "ASELS", "BIMAS", "DOHOL", "EKGYO", "FROTO", "HALKB", "GARAN", "ISCTR", "KCHOL", "KOZAA", "KOZAL",
          "KRDMD", "AKBNK", "PETKM", "PGSUS", "SAHOL", "EREGL", "SODA", "TAVHL", "TCELL", "THYAO", "TKFEN",
          "TOASO", "TSKB", "TTKOM", "TUPRS", "VAKBN", "YKBNK"]

use_date = ['201911', '201912', '202001', '202002', '202003',
            '202004', '202005', '202006', '202007', '202008',
            '202009', '202010', '202011', '202012', '202101']

# BIST30 = ["ARCLK", "ASELS", "BIMAS", "DOHOL", "EKGYO"]
#
# use_date = ['201911', '201912', '202001']

use_cols = ['symbol', 'time', 'bid_price', 'ask_price']

date_columns = 'time'

start_time = time.time()

all_paths = list(glob.iglob(folder_path + '**/eq/*.csv', recursive=True))

path = all_paths[0]

path_df = pd.Series(all_paths).str.split('\\', expand=True)

path_df.columns = ['main_path', 'year', 'year_month', 'sub_dir', 'file_name']

path_df['symbol'] = path_df['file_name'].str.split('_', expand=True)[1].str.split('.', expand=True)[0]

path_df['path'] = all_paths

path_df = path_df[path_df['year_month'].isin(use_date)]

path_bist30 = path_df[path_df['symbol'].isin(BIST30)]

count = 0


def read_data(_path: str) -> pd.DataFrame:
    global count
    count = count + 1
    print(count, '. veri okunuyor -> ', _path)
    try:
        return pd.read_csv(_path, usecols=use_cols, converters={date_columns: lambda x: pd.Timestamp(int(x))})
    except pd.errors.EmptyDataError:
        print("Empty Data:\n", _path)


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=8)
    results = pool.map(read_data, path_bist30.path)

    data = pd.concat(results)

    data.to_csv('data.csv', index=False)

    print("___%s seconds ___" % (time.time() - start_time))
