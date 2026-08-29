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
    print('DATA INSPECTION')
    df_raw.info()
    print('\n')
    print('SHAPE')
    print(df_raw.shape)
    print('\n')
    print('NUMERICAL DESCRIPTION')
    print(df_raw.describe(include='number'))
    print('\n')

    #missing values
    print('MISSING VALUES')
    print(df_raw.isna().sum())
    print('\n')

    #duplicates
    print('duplicates:', df_raw.duplicated().sum())
    print('\n')

def inspect_categorical(df_raw):

    print('CATEGORICAL INSPECTION')
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
    print('\n')

def remove_subunits(df_raw):

    print('SUBUNITS REMOVED')
    condition = df_raw['unit']==0
    df_filtered = df_raw[condition]

    initial_rows = len(df_raw['unit'])
    filtered_rows = len(df_filtered)
    removed_rows = initial_rows - filtered_rows

    print('initial_rows:', initial_rows)
    print('filtered_rows:', filtered_rows)
    print('removed_rows:', removed_rows)

    return df_filtered

def inspect_quality_variables(df_clean):

    print('QUALITY VARIABLES INSPECTION')
    print('\n')

    print(df_clean['category'].value_counts())
    print('\n')
    print(df_clean['is_outlier'].value_counts())
    print('\n')
    print(df_clean['price_is_range'].value_counts())

def apply_quality_filters(df_clean):

    print('QUALITY FILTERS APPLIED')

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

    print('MISSING VALUES INSPECTION')
     
    print('price missing values:', df_clean['price'].isna().sum())
    print('surface_mq missing values:', df_clean['surface_mq'].isna().sum())
    print('price_per_mq missing values:', df_clean['price_per_mq'].isna().sum())

def encode_elevator(df_clean):
    df_clean['elevator'] = df_clean['elevator'].fillna(0)

    return df_clean

def inspect_text_variables(df_clean):
    print('TEXT VARIABLES INSPECTION')
    print('\n')
    print(df_clean['rooms'].value_counts())
    print('\n')
    print(df_clean['bathrooms'].value_counts())
    print('\n')
    print(df_clean['floor'].value_counts().head(5))

def parse_text_variables(df_clean):

    print('TEXT VARIABLES PARSING')

    #rooms
    room_ranges = df_clean['rooms'].str.contains(r'\d+\s*-\s*\d+', na=False)
    df_clean = df_clean[~room_ranges]

    df_clean['rooms'] = df_clean['rooms'].str.extract(r'(\d+)')
    df_clean['rooms'] = pd.to_numeric(df_clean['rooms'])

    #bathrooms
    df_clean['bathrooms'] = df_clean['bathrooms'].str.extract(r'(\d+)')
    df_clean['bathrooms'] = pd.to_numeric(df_clean['bathrooms'])

    #floor
    df_clean['floor'] = df_clean['floor'].str.lower()

    df_clean['floor'] = df_clean['floor'].replace({
        'piano terra': '0',
        'piano rialzato': '0.5'
    })

    df_clean['floor'] = df_clean['floor'].str.extract(
        r'(\d+(?:\.\d+)?)'
    )

    df_clean['floor'] = pd.to_numeric(df_clean['floor'])

    return df_clean

def validate_clean_data(df_clean):

    print('FINAL DATA VALIDATION')
    print('\n')

    #dataset shape
    print('SHAPE')
    print(df_clean.shape)
    print('\n')

    #missing values
    print('MISSING VALUES')
    print(df_clean.isna().sum())
    print('\n')

    #duplicates
    print('DUPLICATES')
    print(df_clean.duplicated().sum())
    print('\n')

    #data types
    print('DATA TYPES')
    print(df_clean.dtypes)
    print('\n')

    #parsed variables
    print('PARSED VARIABLES')
    print(df_clean[['rooms', 'bathrooms', 'floor']].head(5))
    print('\n')

    #transformed variables
    print('TRANSFORMED VARIABLES')
    print('\n')

    print('rooms:')
    print(df_clean['rooms'].value_counts())
    print('\n')

    print('bathrooms:')
    print(df_clean['bathrooms'].value_counts())
    print('\n')

    print('floor:')
    print(df_clean['floor'].value_counts())
    print('\n')

    print('elevator:')
    print(df_clean['elevator'].value_counts())

    return df_clean

def descriptive_statistics(df_clean):

    variables = ['price','surface_mq','price_per_mq']

    descriptive_data = df_clean[variables]

    # Measures of central tendency
    mean = descriptive_data.mean()
    median = descriptive_data.median()
    mode = descriptive_data.mode().iloc[0]

    # Measures of dispersion
    variance = descriptive_data.var()
    std = descriptive_data.std()
    maximum = descriptive_data.max()
    minimum = descriptive_data.min()
    q1 = descriptive_data.quantile(0.25)
    q3 = descriptive_data.quantile(0.75)
    iqr = q3 - q1
    range_ = maximum - minimum
    cv = std/mean
    skewness = descriptive_data.skew()

    #table
    statistics = {
        'Mean': mean,
        'Median': median,
        'Mode': mode,
        'Var': variance,
        'Std': std,
        'Max': maximum,
        'Min': minimum,
        'Q1': q1,
        'Q3': q3,
        'IQR': iqr,
        'Range': range_,
        'CV': cv,
        'Skewness': skewness
    }
    statistics_df = pd.DataFrame(statistics).round(2)

    print(statistics_df)

    return statistics_df

def plot_boxplots(df_clean):

    variables = ['price','surface_mq','price_per_mq']
    box_plot_data = df_clean[variables]

    fig, axes = plt.subplots(1,3)
    axes[0].boxplot(box_plot_data['price'])
    axes[0].set_title('Price')
    axes[0].set_ylabel('Price (€)')

    axes[1].boxplot(box_plot_data['surface_mq'])
    axes[1].set_title('Surface (m²)')
    axes[1].set_ylabel('Surface (m²)')

    axes[2].boxplot(box_plot_data['price_per_mq'])
    axes[2].set_title('Price per m²')
    axes[2].set_ylabel('Price per m² (€ / m²)')

    plt.tight_layout()
    plt.show()

def plot_hist(df_clean):

    variables = ['price', 'surface_mq','price_per_mq']
    hist_data = df_clean[variables]
    mean = hist_data.mean()
    median = hist_data.median()

    fig, axes = plt.subplots(1,3)
    axes[0].hist(hist_data['price'], bins=30)
    axes[0].set_title('Price')
    axes[0].set_ylabel('Frequency')
    axes[0].axvline(mean['price'], linestyle='--', color='red', label='Mean')
    axes[0].axvline(median['price'], linestyle='--', color='green', label='Median')
    axes[0].legend()


    axes[1].hist(hist_data['surface_mq'], bins=30)
    axes[1].set_title('Surface (m²)')
    axes[1].set_ylabel('Frequency')
    axes[1].axvline(mean['surface_mq'], linestyle='--', color='red', label='Mean')
    axes[1].axvline(median['surface_mq'], linestyle='--', color='green', label='Median')
    axes[1].legend()

    axes[2].hist(hist_data['price_per_mq'], bins=30)
    axes[2].set_title('Price per m² (€/m²)')
    axes[2].set_ylabel('Frequency')
    axes[2].axvline(mean['price_per_mq'], linestyle='--', color='red', label='Mean')
    axes[2].axvline(median['price_per_mq'], linestyle='--', color='green', label='Median')
    axes[2].legend()

    plt.tight_layout()
    plt.show()

       













   
#main program

#data inspection
inspect_data(df_raw)
print('\n')
inspect_categorical(df_raw)

#data cleaning

#quality filters
df_clean = remove_subunits(df_raw)
print('\n')
inspect_quality_variables(df_clean)
print('\n')
df_clean = apply_quality_filters(df_clean)
print('\n')

#missing values
inspect_missing_values(df_clean)
print('\n')

#elevator encoding
df_clean = encode_elevator(df_clean)
print(df_clean['elevator'].value_counts())
print('\n')

#Data type / Text parsing
inspect_text_variables(df_clean)
print('\n')
df_clean = parse_text_variables(df_clean)
print('\n')

#final data validation
print('\n')
df_clean = validate_clean_data(df_clean)
print('\n')

# PHASE 1 - DESCRIPTIVE STATISTICS
print('\n')
print('PHASE 1 - DESCRIPTIVE STATISTICS')
print('\n')
descriptive_statistics(df_clean)
print('\n')
plot_boxplots(df_clean)

#PHASE 2 — PROBABILITY & DISTRIBUTIONS
print('\n')
print('PHASE 2 — PROBABILITY & DISTRIBUTIONS')
plot_hist(df_clean)













