import pandas as pd

file = pd.read_csv('./train_result.txt', delimiter = ' ')
file.to_csv('./train.csv', sep=',', na_rep='NaN', index=False)
