import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.oneway import anova_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import seaborn as sns


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

    fig, axes = plt.subplots(1,3, figsize=(15,5))
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
    plt.savefig('charts/boxplots.png', dpi=150)
    plt.show()

def plot_hist(df_clean):

    variables = ['price', 'surface_mq','price_per_mq']
    hist_data = df_clean[variables]
    mean = hist_data.mean()
    median = hist_data.median()

    fig, axes = plt.subplots(1,3, figsize=(15,5))
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
    plt.savefig('charts/histograms.png', dpi=150)
    plt.show()

def plot_qq(df_clean):
    variables = ['price', 'surface_mq', 'price_per_mq']
    qq_data = df_clean[variables]

    fig, axes = plt.subplots(1, 3, figsize=(15,5))
    stats.probplot(qq_data['price'], dist='norm', plot=axes[0])
    axes[0].set_title('Price')

    stats.probplot(qq_data['surface_mq'], dist='norm', plot=axes[1])
    axes[1].set_title('Surface (m²)')

    stats.probplot(qq_data['price_per_mq'], dist='norm', plot=axes[2])
    axes[2].set_title('Price per m² (€/m²)')

    plt.tight_layout()
    plt.savefig('charts/qq_plots.png', dpi=150)
    plt.show()

def percentile_statistics(df_clean):
    variables = ['price', 'surface_mq', 'price_per_mq']
    percentile_data = df_clean[variables]

    #percentile calculation
    p1 = percentile_data.quantile(0.01)
    p5 = percentile_data.quantile(0.05)
    p10 = percentile_data.quantile(0.10)
    p25 = percentile_data.quantile(0.25)
    p50 = percentile_data.quantile(0.50)
    p75 = percentile_data.quantile(0.75)
    p90 = percentile_data.quantile(0.90)
    p95 = percentile_data.quantile(0.95)
    p99 = percentile_data.quantile(0.99)

    #table
    percentiles = {
        'P1': p1,
        'P5': p5,
        'P10': p10,
        'P25': p25,
        'P50': p50,
        'P75': p75,
        'P90': p90,
        'P95': p95,
        'P99': p99,
    }

    percentile_df = pd.DataFrame(percentiles).round(2)
    print(percentile_df)

    return percentile_df

def distribution_shape(df_clean):
     variables = ['price', 'surface_mq', 'price_per_mq']
     shape_data = df_clean[variables]
     kurtosis = shape_data.kurt()
     skewness = shape_data.skew()

     shape_statistics = {
         'Skewness': skewness,
         'Kurtosis': kurtosis
     }

     shape_df = pd.DataFrame(shape_statistics).round(2)
     print(shape_df)

     return shape_df

def plot_normal_distribution(df_clean):
    variables = ['price', 'surface_mq', 'price_per_mq']
    normal_data = df_clean[variables]
    mean_price = normal_data['price'].mean()
    std_price = normal_data['price'].std()
    mean_surface = normal_data['surface_mq'].mean()
    std_surface = normal_data['surface_mq'].std()
    mean_price_mq = normal_data['price_per_mq'].mean()
    std_price_mq = normal_data['price_per_mq'].std()

    fig, axes = plt.subplots(1,3, figsize=(15,5))

    #price normal curve
    x_price = np.linspace(normal_data['price'].min(),
                          normal_data['price'].max(), 
                          100)
    normal_curve = stats.norm.pdf(x_price, mean_price, std_price)
    axes[0].hist(normal_data['price'], bins=30, density=True)
    axes[0].plot(x_price, normal_curve)
    axes[0].set_title('Price')

    #surface normal curve
    x_surface = np.linspace(normal_data['surface_mq'].min(),
                              normal_data['surface_mq'].max(), 
                              100)
    normal_curve = stats.norm.pdf(x_surface, mean_surface, std_surface)
    axes[1].hist(normal_data['surface_mq'], bins=30, density=True)
    axes[1].plot(x_surface, normal_curve)
    axes[1].set_title('Surface (m²)')

    #price per mq curve
    x_price_mq = np.linspace(normal_data['price_per_mq'].min(),
                              normal_data['price_per_mq'].max(), 
                              100)
    normal_curve = stats.norm.pdf(x_price_mq, mean_price_mq, std_price_mq)
    axes[2].hist(normal_data['price_per_mq'], bins=30, density=True)
    axes[2].plot(x_price_mq, normal_curve)
    axes[2].set_title('Price per m² (€/m²)')

    plt.tight_layout()
    plt.savefig('charts/normal_distribution.png', dpi=150)
    plt.show()

def log_transform(df_clean):
    log_data = df_clean.copy()
    log_data['log_price'] = np.log(log_data['price'])
    log_skewness = log_data['log_price'].skew()
    log_kurtosis = log_data['log_price'].kurt()
    print('Log Price Skewness:', round(log_skewness, 2))
    print('Log Price Kurtosis:', round(log_kurtosis, 2))

def plot_log_comparison(df_clean):
    log_data = df_clean.copy()
    log_data['log_price'] = np.log(log_data['price'])
    mean_price = log_data['price'].mean()
    std_price = log_data['price'].std()
    mean_log_price = log_data['log_price'].mean()
    std_log_price = log_data['log_price'].std()


    fig, axes = plt.subplots(1,2, figsize=(10,5))

    #plot hist and normal curve price
    x_price = np.linspace(log_data['price'].min(), 
                          log_data['price'].max(), 
                              100)
    normal_curve = stats.norm.pdf(x_price, mean_price, std_price)
    axes[0].hist(log_data['price'], bins=30, density=True)
    axes[0].plot(x_price, normal_curve)
    axes[0].set_title('Price')

    #plot hist log price
    x_log_price = np.linspace(log_data['log_price'].min(),
                              log_data['log_price'].max(), 
                              100)
    normal_curve = stats.norm.pdf(x_log_price, mean_log_price, std_log_price)
    axes[1].hist(log_data['log_price'], bins=30, density=True)
    axes[1].plot(x_log_price, normal_curve)
    axes[1].set_title('Log Price')

    plt.tight_layout()
    plt.savefig('charts/log_comparison.png', dpi=150)
    plt.show()

def population_parameters(df, variable):
    mean = df[variable].mean()
    std = df[variable].std(ddof=0)
    print('mean:', mean)
    print('std:', std)

    return mean, std

def draw_sample(df_clean):

    population_std = df_clean['price_per_mq'].std(ddof=0)

    sample_means_30=[]
    sample_means_100=[]
    sample_means_500=[]

    for i in range(1000):
        sample = df_clean.sample(30, replace=False)
        sample_mean = sample['price_per_mq'].mean()
        sample_means_30.append(sample_mean)

    for i in range(1000):
        sample = df_clean.sample(100, replace=False)
        sample_mean = sample['price_per_mq'].mean()
        sample_means_100.append(sample_mean)

    for i in range(1000):
        sample = df_clean.sample(500, replace=False)
        sample_mean = sample['price_per_mq'].mean()
        sample_means_500.append(sample_mean)

    fig, axes = plt.subplots(1,3, figsize=(15,5), sharex=True)

    axes[0].hist(sample_means_30, bins=30, density=True)
    axes[0].set_title('n = 30')

    axes[1].hist(sample_means_100, bins=30, density=True)
    axes[1].set_title('n = 100')

    axes[2].hist(sample_means_500, bins=30, density=True)
    axes[2].set_title('n = 500')

    plt.tight_layout()
    plt.savefig('charts/sampling_distributions.png', dpi=150)
    plt.show()

    empirical_se_30 = np.std(sample_means_30)
    empirical_se_100 = np.std(sample_means_100)
    empirical_se_500 = np.std(sample_means_500)

    theoretical_se_30 = population_std / np.sqrt(30)
    theoretical_se_100 = population_std / np.sqrt(100)
    theoretical_se_500 = population_std / np.sqrt(500)

    se_data = {
        'n': [30, 100, 500],
        'Empirical SE': [empirical_se_30, empirical_se_100, empirical_se_500],
        'Theorical SE': [theoretical_se_30, theoretical_se_100, theoretical_se_500]
    }

    se_df = pd.DataFrame(se_data)
    print(se_df)

    return se_df

def confidence_intervals(df_clean):

    confidence_level = 0.95
    alpha = 0.05
    n = [30, 100, 500]
    population_mean = df_clean['price_per_mq'].mean()

    intervals_30 = []
    intervals_100 = []
    intervals_500 = []

    for sample_size in n:
        t_critical = stats.t.ppf(1 - alpha/2, df = sample_size-1)

        for i in range(1000):
            sample = df_clean.sample(sample_size, replace=False)
            sample_mean = sample['price_per_mq'].mean()
            sample_std = sample['price_per_mq'].std()

            margin_error = t_critical * (sample_std / np.sqrt(sample_size))
            lower = sample_mean - margin_error
            upper = sample_mean + margin_error

            if sample_size == 30:
                intervals_30.append((lower, upper))

            elif sample_size == 100:
                intervals_100.append((lower, upper))

            else:
                intervals_500.append((lower, upper))

    coverage_30 = 0
    coverage_100 = 0
    coverage_500 = 0

    for lower, upper in intervals_30:
        
        if lower <= population_mean <= upper:
            coverage_30 += 1
            
    coverage_30_percent = coverage_30 / 1000 * 100

    for lower, upper in intervals_100:

        if lower <= population_mean <= upper:
            coverage_100 += 1 

    coverage_100_percent = coverage_100 / 1000 * 100

    for lower, upper in intervals_500:
    
            if lower <= population_mean <= upper:
                coverage_500 += 1 
    coverage_500_percent = coverage_500 / 1000 * 100

    print('Coverage 30:', round(coverage_30_percent, 2), '%')
    print('Coverage 100:', round(coverage_100_percent, 2), '%')
    print('Coverage 500:', round(coverage_500_percent, 2), '%')

def two_sample_test(group_1, group_2):

    levene = stats.levene(group_1, group_2)

    t_test = stats.ttest_ind(
        group_1,
        group_2,
        equal_var=False
    )

    mean_1 = group_1.mean()
    mean_2 = group_2.mean()

    std_1 = group_1.std()
    std_2 = group_2.std()

    n_1 = len(group_1)
    n_2 = len(group_2)

    mean_diff = mean_1 - mean_2

    se_mean_diff = np.sqrt(
        (std_1**2 / n_1) +
        (std_2**2 / n_2)
    )

    degrees_freedom = (
        (std_1**2 / n_1 + std_2**2 / n_2)**2 /
        (
            (std_1**2 / n_1)**2 / (n_1 - 1) +
            (std_2**2 / n_2)**2 / (n_2 - 1)
        )
    )

    t_critical = stats.t.ppf(0.975, degrees_freedom)

    margin_error = t_critical * se_mean_diff

    lower = mean_diff - margin_error
    upper = mean_diff + margin_error

    pooled_std = np.sqrt(
        (
            (n_1 - 1) * std_1**2 +
            (n_2 - 1) * std_2**2
        ) /
        (n_1 + n_2 - 2)
    )

    cohens_d = mean_diff / pooled_std

    return levene, t_test, degrees_freedom, (lower, upper), cohens_d

def hypothesis_testing(df_clean):
    centro = df_clean[df_clean['macrozone'] == 'Centro']['price_per_mq']
    periferia = df_clean[df_clean['macrozone'] == 'Bisceglie, Baggio, Olmi']['price_per_mq']
    ripamonti_vigentino = df_clean[df_clean['macrozone'] == 'Ripamonti, Vigentino']['price_per_mq']
    porta_vittoria_lodi = df_clean[df_clean['macrozone'] == 'Porta Vittoria, Lodi']['price_per_mq']
    elevator_yes = df_clean[df_clean['elevator'] == 1]['price_per_mq']
    elevator_no = df_clean[df_clean['elevator'] == 0]['price_per_mq']
    da_ristrutturare = df_clean[df_clean['condition'] == 'Da ristrutturare']['price_per_mq']
    ottimo_ristrutturato = df_clean[df_clean['condition'] == 'Ottimo / Ristrutturato']['price_per_mq']

    # TEST 1 - TWO ZONES
    print('TEST 1 — Two Zones')

    # far macrozones
    test_zones = two_sample_test(centro, periferia)

    print('centro vs periferia')
    print('Levene:', test_zones[0])
    print('t-statistic:', test_zones[1].statistic)
    print('p-value:', test_zones[1].pvalue)
    print('Degrees of freedom:', test_zones[2])
    print('95% CI:', test_zones[3])
    print("Cohen's d:", test_zones[4])
    print('\n')

    #near macrozones
    test_zones_2 = two_sample_test(ripamonti_vigentino, porta_vittoria_lodi)

    print('Ripamonti, Vigentino vs Porta Vittoria, Lodi')
    print('Levene:', test_zones_2[0])
    print('t-statistic:', test_zones_2[1].statistic)
    print('p-value:', test_zones_2[1].pvalue)
    print('Degrees of freedom:', test_zones_2[2])
    print('95% CI:', test_zones_2[3])
    print("Cohen's d:", test_zones_2[4])
    print('\n')

    #TEST 2 - A PROPERTY CHARACTERISTIC
    print('TEST 2 — A property characteristic')

    #elevator
    print('Elevator: yes vs no')
    elevator_test = two_sample_test(elevator_yes, elevator_no)
    
    print('Levene:', elevator_test[0])
    print('t-statistic:', elevator_test[1].statistic)
    print('p-value:', elevator_test[1].pvalue)
    print('Degrees of freedom:', elevator_test[2])
    print('95% CI:', elevator_test[3])
    print("Cohen's d:", elevator_test[4])
    print('\n')
    
    #condition
    print('Condition: Da ristrutturare vs Ottimo/Ristrutturato')
    condition_test = two_sample_test(da_ristrutturare, ottimo_ristrutturato)

    print('Levene:', condition_test[0])
    print('t-statistic:', condition_test[1].statistic)
    print('p-value:', condition_test[1].pvalue)
    print('Degrees of freedom:', condition_test[2])
    print('95% CI:', condition_test[3])
    print("Cohen's d:", condition_test[4])

def anova_analysis(df_clean):

    anova_data = df_clean[['price_per_mq', 'macrozone']].dropna()

    groups = [
        group['price_per_mq'].values
        for name, group in anova_data.groupby('macrozone')
    ]

    anova_result = stats.f_oneway(*groups)

    grand_mean = anova_data['price_per_mq'].mean()

    between_variation = sum(
        len(group) * (group['price_per_mq'].mean() - grand_mean)**2
        for name, group in anova_data.groupby('macrozone')
    )

    total_variation = sum(
        (anova_data['price_per_mq'] - grand_mean)**2
    )

    eta_squared = between_variation / total_variation

    print('ANOVA - 32 MACROZONES')

    print('F-statistic:', anova_result.statistic)

    print('Degrees of freedom:', len(groups) - 1,
          ',', len(anova_data) - len(groups))

    print('p-value:', anova_result.pvalue)

    print('Eta squared:', eta_squared)

    return anova_result, eta_squared

def welch_anova(df_clean):

    anova_data = df_clean[['price_per_mq', 'macrozone']].dropna()

    groups = [
        group['price_per_mq'].values
        for name, group in anova_data.groupby('macrozone')
    ]

    levene_result = stats.levene(*groups)

    welch_result = anova_oneway(
        anova_data['price_per_mq'],
        groups=anova_data['macrozone'],
        use_var='unequal'
    )

    print('ASSUMPTION CHECK')

    print('Levene:', levene_result)

    print('\n')

    print('WELCH ANOVA')

    print('F-statistic:', welch_result.statistic)

    print('Degrees of freedom:', welch_result.df)

    print('p-value:', welch_result.pvalue)

    return levene_result, welch_result

def residual_diagnostics(df_clean):

    residual_data = df_clean[['price_per_mq', 'macrozone']].dropna()

    model = sm.formula.ols(
        'price_per_mq ~ C(macrozone)',
        data=residual_data
    ).fit()

    fitted_values = model.fittedvalues
    residuals = model.resid

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].scatter(fitted_values, residuals)

    axes[0].axhline(0, linestyle='--')

    axes[0].set_title('Residuals vs Fitted')

    axes[0].set_xlabel('Fitted Values')

    axes[0].set_ylabel('Residuals')

    stats.probplot(
        residuals,
        dist='norm',
        plot=axes[1]
    )

    axes[1].set_title('Q-Q Plot of Residuals')

    plt.tight_layout()

    plt.savefig('charts/anova_residuals.png', dpi=150)

    plt.show()

    return model

def tukey_posthoc(df_clean):

    tukey_data = df_clean[['price_per_mq', 'macrozone']].dropna()

    tukey_result = pairwise_tukeyhsd(
        endog=tukey_data['price_per_mq'],
        groups=tukey_data['macrozone'],
        alpha=0.05
    )

    tukey_table = pd.DataFrame(
        data=tukey_result._results_table.data[1:],
        columns=tukey_result._results_table.data[0]
    )

    significant_pairs = tukey_table[
        tukey_table['reject'] == True
    ]

    print('TUKEY HSD')

    print('Total comparisons:', len(tukey_table))

    print('Significant comparisons:', len(significant_pairs))

    print('\n')

    print('Most significant pairs')

    significant_pairs = significant_pairs.copy()

    significant_pairs['abs_meandiff'] = (
        significant_pairs['meandiff'].abs()
    )

    significant_pairs = significant_pairs.sort_values(
        'abs_meandiff',
        ascending=False
    )

    print(
        significant_pairs[
            ['group1', 'group2', 'meandiff', 'p-adj', 'reject']
        ].head(10)
    )

    return tukey_result, significant_pairs

def plot_macrozone_boxplots(df_clean):

    boxplot_data = df_clean[['price_per_mq', 'macrozone']].dropna()

    macrozone_order = (
        boxplot_data
        .groupby('macrozone')['price_per_mq']
        .median()
        .sort_values()
        .index
    )

    data = [
        boxplot_data[
            boxplot_data['macrozone'] == macrozone
        ]['price_per_mq']
        for macrozone in macrozone_order
    ]

    plt.figure(figsize=(16, 8))

    plt.boxplot(
    data,
    tick_labels=macrozone_order
)

    plt.title('Price per m² by Macrozone')

    plt.xlabel('Macrozone')

    plt.ylabel('Price per m² (€ / m²)')

    plt.xticks(rotation=90)

    plt.tight_layout()

    plt.savefig('charts/macrozone_boxplots.png', dpi=150)

    plt.show()

def anova_phase(df_clean):

    print('PHASE 5 - ANOVA')

    print('\n')

    anova_analysis(df_clean)

    print('\n')

    welch_anova(df_clean)

    print('\n')

    residual_diagnostics(df_clean)

    print('\n')

    tukey_posthoc(df_clean)

    print('\n')

    plot_macrozone_boxplots(df_clean)

def prepare_correlation_data(df_clean):

    correlation_data = df_clean.copy()

    condition_mapping = {
        'Da ristrutturare': 1,
        'Buono / Abitabile': 2,
        'Ottimo / Ristrutturato': 3,
        'Nuovo / In costruzione': 4
    }

    correlation_data['condition_numeric'] = (
        correlation_data['condition']
        .map(condition_mapping)
    )

    return correlation_data

def correlation_analysis(df_clean):

    correlation_data = prepare_correlation_data(df_clean)

    variables = [
        'surface_mq',
        'rooms',
        'bathrooms',
        'condition_numeric',
        'floor'
    ]

    print('CORRELATION WITH PRICE')

    for variable in variables:

        data = correlation_data[
            [variable, 'price']
        ].dropna()

        pearson = stats.pearsonr(
            data[variable],
            data['price']
        )

        spearman = stats.spearmanr(
            data[variable],
            data['price']
        )

        print('\n')

        print(variable)

        print('Pearson:', pearson.statistic)

        print('Pearson p-value:', pearson.pvalue)

        print('Spearman:', spearman.statistic)

        print('Spearman p-value:', spearman.pvalue)

def correlation_matrix(df_clean):

    correlation_data = prepare_correlation_data(df_clean)

    variables = [
        'price',
        'surface_mq',
        'rooms',
        'bathrooms',
        'condition_numeric',
        'floor'
    ]

    correlation_matrix = correlation_data[
        variables
    ].corr(method='pearson')

    print('\n')

    print('CORRELATION MATRIX')

    print(correlation_matrix)

    plt.figure(figsize=(10, 8))

    sns.heatmap(
        correlation_matrix,
        annot=True,
        fmt='.2f',
        cmap='coolwarm',
        center=0
    )

    plt.title('Correlation Matrix')

    plt.tight_layout()

    plt.savefig(
        'charts/correlation_matrix.png',
        dpi=150
    )

    plt.show()

    return correlation_matrix

def pearson_spearman_comparison(df_clean):

    correlation_data = prepare_correlation_data(df_clean)

    variables = [
        'surface_mq',
        'rooms',
        'bathrooms',
        'condition_numeric',
        'floor'
    ]

    pearson_values = []
    spearman_values = []

    for variable in variables:

        data = correlation_data[
            [variable, 'price']
        ].dropna()

        pearson = stats.pearsonr(
            data[variable],
            data['price']
        ).statistic

        spearman = stats.spearmanr(
            data[variable],
            data['price']
        ).statistic

        pearson_values.append(pearson)

        spearman_values.append(spearman)

    comparison = pd.DataFrame({
        'variable': variables,
        'Pearson': pearson_values,
        'Spearman': spearman_values
    })

    print('\n')

    print('PEARSON VS SPEARMAN')

    print(comparison)

    x = np.arange(len(variables))

    width = 0.35

    plt.figure(figsize=(10, 6))

    plt.bar(
        x - width / 2,
        pearson_values,
        width,
        label='Pearson'
    )

    plt.bar(
        x + width / 2,
        spearman_values,
        width,
        label='Spearman'
    )

    plt.axhline(0, linestyle='--')

    plt.xticks(
        x,
        variables,
        rotation=45
    )

    plt.ylabel('Correlation with Price')

    plt.title('Pearson vs Spearman Correlation')

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        'charts/pearson_spearman_comparison.png',
        dpi=150
    )

    plt.show()

    return comparison

def correlation_phase(df_clean):

    print('PHASE 6 - CORRELATION')

    print('\n')

    correlation_analysis(df_clean)

    print('\n')

    correlation_matrix(df_clean)

    print('\n')

    pearson_spearman_comparison(df_clean)

   








    

            

    
       

       
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
print('\n')
plot_hist(df_clean)
plot_qq(df_clean)
percentile_statistics(df_clean)
print('\n')
distribution_shape(df_clean)
plot_normal_distribution(df_clean)
print('\n')
log_transform(df_clean)
plot_log_comparison(df_clean)
print('\n')
print('\n')

#PHASE 3 - SAMPLING & CONFIDENCE INTERVALS
print('PHASE 3 - SAMPLING & CONFIDENCE INTERVALS')
print('\n')
population_parameters(df_clean, 'price_per_mq')
print('\n')
draw_sample(df_clean)
print('\n')
confidence_intervals(df_clean)
print('\n')
print('\n')

#PHASE 4 - HYPOTHESIS TESTING
print('PHASE 4 - HYPOTHESIS TESTING')
print('\n')
hypothesis_testing(df_clean)
print('\n')

# PHASE 5 - ANOVA
print('\n')
anova_phase(df_clean)
print('\n')

# PHASE 6 - CORRELATION

print('\n')
correlation_phase(df_clean)
print('\n')



















