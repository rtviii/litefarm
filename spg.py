import pandas as pd

x = pd.read_excel('./SPG LiteFarm Census Data.xlsx')
print(x[['Farm ID', 'User ID', 'Associated Email Address']])


