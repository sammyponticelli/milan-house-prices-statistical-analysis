import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import statsmodels.api as sm
from scipy import stats

#load data
df_raw = pd.read_csv('immobiliare_milano_vendita.csv')

#initial inspection
def inspect_data(df_raw):

    #general info
    df_raw.info()
    print(df_raw.shape)
    print('\n')
    print(df_raw.describe(include='number'))

    #missing values
    print(df_raw.isna().sum())
    print('\n')

    #duplicates
    print(df_raw.duplicated().sum())
    print('\n')

    #categorical variables
    print(df_raw['category'].value_counts())
    print('\n')
    print(df_raw['unit'].value_counts())
    print('\n')
    print(df_raw['condition'].value_counts())
    print('\n')
    print(df_raw['heating'].value_counts())
    print('\n')
    print(df_raw['typology'].value_counts())
    print('\n')
    print(df_raw['elevator'].value_counts())

def remove_subunits(df_raw):
    condition = df_raw['unit']==0
    df_filtered = df_raw[condition]

    initial_rows = len(df_raw['unit'])
    filtered_rows = len(df_filtered)
    removed_rows = initial_rows - filtered_rows

    print(df_filtered)
    print('\n')
    print('initial_rows:', initial_rows)
    print('filtered_rows:', filtered_rows)
    print('removed_rows:', removed_rows)

    return df_filtered



#main program
inspect_data(df_raw)
print('\n')
remove_subunits(df_raw)











