import pandas as pd

x = pd.read_excel('spg-filled1.xlsx')
x.to_csv("spg.csv")