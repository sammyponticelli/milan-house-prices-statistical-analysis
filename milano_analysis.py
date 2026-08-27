import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from scipy import stats

#load data
df_raw = pd.read_csv('immobiliare_milano_vendita.csv')

#initial inspection
df_raw.shape
df_raw.info()
df_raw.describe()
df_raw.isna().sum()




