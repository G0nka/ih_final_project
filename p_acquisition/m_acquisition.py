import pandas as pd

# acquisition functions

def acquire_inputs():
    assets = pd.read_csv('./data/raw/Assets_2020Q4.csv')
    cf_liabs = pd.read_csv('./data/raw/Liabilities_2020Q4.csv')
    return assets, cf_liabs
