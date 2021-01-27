import pandas as pd

data = pd.read_csv('../rol300_noint_5min_thr1_std.csv')

data.duration_trades_median = pd.to_timedelta(data.duration_trades_median)
data.duration_trades_mean = pd.to_timedelta(data.duration_trades_mean)

data = data.sort_values('c_return', ascending=False)

average = data.mean()

num_positive = data[data.c_return > 0].count()

avg_positive = data[data.c_return > 0].mean()

avg_20 = data.head(20).mean()

result = pd.DataFrame([average, avg_positive, avg_20, num_positive], index=['avg', 'positive', 'avg_20', 'num']).drop(
    'name', axis=1)

