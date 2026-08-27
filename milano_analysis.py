import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from scipy import stats

#load data
df_raw = pd.read_csv('immobiliare_milano_vendita.csv')

#initial inspection
def inspect_data(df_raw):

    #general info
    df_raw.info()
    print(df_raw.shape)
    print(df_raw.describe())

    print()

    #missing values
    print(df_raw.isna().sum())

    print()

    #duplicates
    print(df_raw.duplicated().sum())

    print()

    #categorical variables
    print(df_raw['category'].value_counts())
    print(df_raw['unit'].value_counts())
    print(df_raw['condition'].value_counts())
    print(df_raw['heating'].value_counts())
    print(df_raw['typology'].value_counts())
    print(df_raw['elevator'].value_counts())

#main program
inspect_data(df_raw)











