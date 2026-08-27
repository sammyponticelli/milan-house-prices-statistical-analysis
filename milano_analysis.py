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

def inspect_categorical(df_raw):

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

def inspect_quality_variables(df_clean):

    print(df_clean['category'].value_counts())
    print('\n')
    print(df_clean['is_outlier'].value_counts())
    print('\n')
    print(df_clean['price_is_range'].value_counts())

def apply_quality_filters(df_clean):

    initial_rows = len(df_clean)
    print('initial rows:', initial_rows)

    #category filter
    condition = df_clean['category']=='Residenziale'
    df_filtered = df_clean[condition]
    print('category rows:', len(df_filtered))

    #is_outlier filter
    condition = df_filtered['is_outlier']==0
    df_filtered = df_filtered[condition]
    print('is_outlier rows:', len(df_filtered))

    #price_is_range filter
    condition = df_filtered['price_is_range']==0
    df_filtered = df_filtered[condition]
    print('price_is_range rows:', len(df_filtered))

    print('final rows:', len(df_filtered))
    removed_rows = initial_rows - len(df_filtered)
    print('removed rows:', removed_rows)

    return df_filtered

def inspect_missing_values(df_clean):
     
    print(df_clean['price'].isna().sum())
    print('\n')
    print(df_clean['surface_mq'].isna().sum())
    print('\n')
    print(df_clean['price_per_mq'].isna().sum())






   
#main program

#data inspection
inspect_data(df_raw)
print('\n')
inspect_categorical(df_raw)

#data cleaning
df_clean = remove_subunits(df_raw)
print('\n')
inspect_quality_variables(df_clean)
print('\n')
df_clean = apply_quality_filters(df_clean)
print('\n')
inspect_missing_values(df_clean)












