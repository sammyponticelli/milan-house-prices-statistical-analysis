import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.oneway import anova_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import seaborn as sns
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

# matplotlib's defaults size text for a figure viewed at its natural size. These
# are read scaled down — on GitHub, and on a phone where the feed is about 350px
# wide — so everything is set a few points larger than the default.
plt.rcParams.update({
    'font.size': 13,
    'axes.titlesize': 16,
    'axes.titleweight': 'semibold',
    'axes.labelsize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 12,
    'figure.constrained_layout.use': False,
    'savefig.bbox': 'tight',
})

# load data
df_raw = pd.read_csv('immobiliare_milano_vendita.csv')


# initial inspection
def inspect_data(df_raw):

    # general info
    print('DATA INSPECTION')
    df_raw.info()
    print('\n')
    print('SHAPE')
    print(df_raw.shape)
    print('\n')
    print('NUMERICAL DESCRIPTION')
    print(df_raw.describe(include='number'))
    print('\n')

    # missing values
    print('MISSING VALUES')
    print(df_raw.isna().sum())
    print('\n')

    # duplicates
    print('duplicates:', df_raw.duplicated().sum())
    print('\n')


def inspect_categorical(df_raw):

    print('CATEGORICAL INSPECTION')
    print('\n')

    # categorical variables
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
    condition = df_raw['unit'] == 0
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

    # category filter
    condition = df_clean['category'] == 'Residenziale'
    df_filtered = df_clean[condition]
    print('category rows:', len(df_filtered))

    # is_outlier filter
    condition = df_filtered['is_outlier'] == 0
    df_filtered = df_filtered[condition]
    print('is_outlier rows:', len(df_filtered))

    # price_is_range filter
    condition = df_filtered['price_is_range'] == 0
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

    # rooms
    room_ranges = df_clean['rooms'].str.contains(r'\d+\s*-\s*\d+', na=False)
    df_clean = df_clean[~room_ranges]

    df_clean['rooms'] = df_clean['rooms'].str.extract(r'(\d+)')
    df_clean['rooms'] = pd.to_numeric(df_clean['rooms'])

    # bathrooms
    df_clean['bathrooms'] = df_clean['bathrooms'].str.extract(r'(\d+)')
    df_clean['bathrooms'] = pd.to_numeric(df_clean['bathrooms'])

    # floor
    df_clean['floor'] = df_clean['floor'].str.lower()

    df_clean['floor'] = df_clean['floor'].replace(
        {'piano terra': '0', 'piano rialzato': '0.5'}
    )

    df_clean['floor'] = df_clean['floor'].str.extract(r'(\d+(?:\.\d+)?)')

    df_clean['floor'] = pd.to_numeric(df_clean['floor'])

    return df_clean


def validate_clean_data(df_clean):

    print('FINAL DATA VALIDATION')
    print('\n')

    # dataset shape
    print('SHAPE')
    print(df_clean.shape)
    print('\n')

    # missing values
    print('MISSING VALUES')
    print(df_clean.isna().sum())
    print('\n')

    # duplicates
    print('DUPLICATES')
    print(df_clean.duplicated().sum())
    print('\n')

    # data types
    print('DATA TYPES')
    print(df_clean.dtypes)
    print('\n')

    # parsed variables
    print('PARSED VARIABLES')
    print(df_clean[['rooms', 'bathrooms', 'floor']].head(5))
    print('\n')

    # transformed variables
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


def data_cleaning_phase(df_raw):

    # data inspection
    inspect_data(df_raw)
    print('\n')
    inspect_categorical(df_raw)

    # quality filters
    df_clean = remove_subunits(df_raw)
    print('\n')
    inspect_quality_variables(df_clean)
    print('\n')
    df_clean = apply_quality_filters(df_clean)
    print('\n')

    # missing values
    inspect_missing_values(df_clean)
    print('\n')

    # elevator encoding
    df_clean = encode_elevator(df_clean)
    print(df_clean['elevator'].value_counts())
    print('\n')

    # data type / text parsing
    inspect_text_variables(df_clean)
    print('\n')
    df_clean = parse_text_variables(df_clean)
    print('\n')

    # final data validation
    print('\n')
    df_clean = validate_clean_data(df_clean)
    print('\n')

    return df_clean


def descriptive_statistics(df_clean):

    variables = ['price', 'surface_mq', 'price_per_mq']

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
    cv = std / mean
    skewness = descriptive_data.skew()

    # table
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
        'Skewness': skewness,
    }
    statistics_df = pd.DataFrame(statistics).round(2)

    print(statistics_df)

    return statistics_df


def plot_boxplots(df_clean):

    variables = ['price', 'surface_mq', 'price_per_mq']
    box_plot_data = df_clean[variables]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
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


def descriptive_statistics_phase(df_clean):

    print('\n')
    print('PHASE 1 - DESCRIPTIVE STATISTICS')
    print('\n')
    descriptive_statistics(df_clean)
    print('\n')
    plot_boxplots(df_clean)


def plot_hist(df_clean):

    variables = ['price', 'surface_mq', 'price_per_mq']
    hist_data = df_clean[variables]
    mean = hist_data.mean()
    median = hist_data.median()

    # stacked rather than side by side: three panels in a row make a 3:1 strip
    # in which nothing survives being scaled down
    fig, axes = plt.subplots(3, 1, figsize=(9, 12))
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
    axes[2].axvline(
        median['price_per_mq'], linestyle='--', color='green', label='Median'
    )
    axes[2].legend()

    plt.tight_layout()
    plt.savefig('charts/histograms.png', dpi=150)
    plt.show()


def plot_qq(df_clean):
    variables = ['price', 'surface_mq', 'price_per_mq']
    qq_data = df_clean[variables]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
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

    # percentile calculation
    p1 = percentile_data.quantile(0.01)
    p5 = percentile_data.quantile(0.05)
    p10 = percentile_data.quantile(0.10)
    p25 = percentile_data.quantile(0.25)
    p50 = percentile_data.quantile(0.50)
    p75 = percentile_data.quantile(0.75)
    p90 = percentile_data.quantile(0.90)
    p95 = percentile_data.quantile(0.95)
    p99 = percentile_data.quantile(0.99)

    # table
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

    shape_statistics = {'Skewness': skewness, 'Kurtosis': kurtosis}

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

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # price normal curve
    x_price = np.linspace(normal_data['price'].min(), normal_data['price'].max(), 100)
    normal_curve = stats.norm.pdf(x_price, mean_price, std_price)
    axes[0].hist(normal_data['price'], bins=30, density=True)
    axes[0].plot(x_price, normal_curve)
    axes[0].set_title('Price')

    # surface normal curve
    x_surface = np.linspace(
        normal_data['surface_mq'].min(), normal_data['surface_mq'].max(), 100
    )
    normal_curve = stats.norm.pdf(x_surface, mean_surface, std_surface)
    axes[1].hist(normal_data['surface_mq'], bins=30, density=True)
    axes[1].plot(x_surface, normal_curve)
    axes[1].set_title('Surface (m²)')

    # price per mq curve
    x_price_mq = np.linspace(
        normal_data['price_per_mq'].min(), normal_data['price_per_mq'].max(), 100
    )
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

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # plot hist and normal curve price
    x_price = np.linspace(log_data['price'].min(), log_data['price'].max(), 100)
    normal_curve = stats.norm.pdf(x_price, mean_price, std_price)
    axes[0].hist(log_data['price'], bins=30, density=True)
    axes[0].plot(x_price, normal_curve)
    axes[0].set_title('Price')

    # plot hist log price
    x_log_price = np.linspace(
        log_data['log_price'].min(), log_data['log_price'].max(), 100
    )
    normal_curve = stats.norm.pdf(x_log_price, mean_log_price, std_log_price)
    axes[1].hist(log_data['log_price'], bins=30, density=True)
    axes[1].plot(x_log_price, normal_curve)
    axes[1].set_title('Log Price')

    plt.tight_layout()
    plt.savefig('charts/log_comparison.png', dpi=150)
    plt.show()


def distribution_phase(df_clean):

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


def population_parameters(df, variable):
    mean = df[variable].mean()
    std = df[variable].std(ddof=0)
    print('mean:', mean)
    print('std:', std)

    return mean, std


def draw_sample(df_clean):

    population_std = df_clean['price_per_mq'].std(ddof=0)

    # same seed at every run, but the generator advances at every draw
    rng = np.random.default_rng(42)

    sample_means_30 = []
    sample_means_100 = []
    sample_means_500 = []

    for i in range(1000):
        sample = df_clean.sample(30, replace=False, random_state=rng)
        sample_mean = sample['price_per_mq'].mean()
        sample_means_30.append(sample_mean)

    for i in range(1000):
        sample = df_clean.sample(100, replace=False, random_state=rng)
        sample_mean = sample['price_per_mq'].mean()
        sample_means_100.append(sample_mean)

    for i in range(1000):
        sample = df_clean.sample(500, replace=False, random_state=rng)
        sample_mean = sample['price_per_mq'].mean()
        sample_means_500.append(sample_mean)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharex=True)

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
        'Theorical SE': [theoretical_se_30, theoretical_se_100, theoretical_se_500],
    }

    se_df = pd.DataFrame(se_data)
    print(se_df)

    return se_df


def confidence_intervals(df_clean):

    confidence_level = 0.95
    alpha = 0.05
    n = [30, 100, 500]
    population_mean = df_clean['price_per_mq'].mean()

    # same seed at every run, but the generator advances at every draw
    rng = np.random.default_rng(42)

    intervals_30 = []
    intervals_100 = []
    intervals_500 = []

    for sample_size in n:
        t_critical = stats.t.ppf(1 - alpha / 2, df=sample_size - 1)

        for i in range(1000):
            sample = df_clean.sample(sample_size, replace=False, random_state=rng)
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


def sampling_phase(df_clean):

    print('PHASE 3 - SAMPLING & CONFIDENCE INTERVALS')
    print('\n')
    population_parameters(df_clean, 'price_per_mq')
    print('\n')
    draw_sample(df_clean)
    print('\n')
    confidence_intervals(df_clean)
    print('\n')
    print('\n')


def two_sample_test(group_1, group_2):

    levene = stats.levene(group_1, group_2)
    t_test = stats.ttest_ind(group_1, group_2, equal_var=False)

    mean_1 = group_1.mean()
    mean_2 = group_2.mean()
    std_1 = group_1.std()
    std_2 = group_2.std()
    n_1 = len(group_1)
    n_2 = len(group_2)

    mean_diff = mean_1 - mean_2
    se_mean_diff = np.sqrt((std_1**2 / n_1) + (std_2**2 / n_2))
    degrees_freedom = (std_1**2 / n_1 + std_2**2 / n_2) ** 2 / (
        (std_1**2 / n_1) ** 2 / (n_1 - 1) + (std_2**2 / n_2) ** 2 / (n_2 - 1)
    )

    t_critical = stats.t.ppf(0.975, degrees_freedom)
    margin_error = t_critical * se_mean_diff
    lower = mean_diff - margin_error
    upper = mean_diff + margin_error

    pooled_std = np.sqrt(
        ((n_1 - 1) * std_1**2 + (n_2 - 1) * std_2**2) / (n_1 + n_2 - 2)
    )
    cohens_d = mean_diff / pooled_std

    return levene, t_test, degrees_freedom, (lower, upper), cohens_d


def hypothesis_testing(df_clean):
    centro = df_clean[df_clean['macrozone'] == 'Centro']['price_per_mq']
    periferia = df_clean[df_clean['macrozone'] == 'Bisceglie, Baggio, Olmi'][
        'price_per_mq'
    ]
    ripamonti_vigentino = df_clean[df_clean['macrozone'] == 'Ripamonti, Vigentino'][
        'price_per_mq'
    ]
    porta_vittoria_lodi = df_clean[df_clean['macrozone'] == 'Porta Vittoria, Lodi'][
        'price_per_mq'
    ]
    elevator_yes = df_clean[df_clean['elevator'] == 1]['price_per_mq']
    elevator_no = df_clean[df_clean['elevator'] == 0]['price_per_mq']
    da_ristrutturare = df_clean[df_clean['condition'] == 'Da ristrutturare'][
        'price_per_mq'
    ]
    ottimo_ristrutturato = df_clean[df_clean['condition'] == 'Ottimo / Ristrutturato'][
        'price_per_mq'
    ]

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

    # near macrozones
    test_zones_2 = two_sample_test(ripamonti_vigentino, porta_vittoria_lodi)

    print('Ripamonti, Vigentino vs Porta Vittoria, Lodi')
    print('Levene:', test_zones_2[0])
    print('t-statistic:', test_zones_2[1].statistic)
    print('p-value:', test_zones_2[1].pvalue)
    print('Degrees of freedom:', test_zones_2[2])
    print('95% CI:', test_zones_2[3])
    print("Cohen's d:", test_zones_2[4])
    print('\n')

    # TEST 2 - A PROPERTY CHARACTERISTIC
    print('TEST 2 — A property characteristic')

    # elevator
    print('Elevator: yes vs no')
    elevator_test = two_sample_test(elevator_yes, elevator_no)

    print('Levene:', elevator_test[0])
    print('t-statistic:', elevator_test[1].statistic)
    print('p-value:', elevator_test[1].pvalue)
    print('Degrees of freedom:', elevator_test[2])
    print('95% CI:', elevator_test[3])
    print("Cohen's d:", elevator_test[4])
    print('\n')

    # condition
    print('Condition: Da ristrutturare vs Ottimo/Ristrutturato')
    condition_test = two_sample_test(da_ristrutturare, ottimo_ristrutturato)

    print('Levene:', condition_test[0])
    print('t-statistic:', condition_test[1].statistic)
    print('p-value:', condition_test[1].pvalue)
    print('Degrees of freedom:', condition_test[2])
    print('95% CI:', condition_test[3])
    print("Cohen's d:", condition_test[4])


def hypothesis_testing_phase(df_clean):

    print('PHASE 4 - HYPOTHESIS TESTING')
    print('\n')
    hypothesis_testing(df_clean)
    print('\n')


def anova_analysis(df_clean):

    anova_data = df_clean[['price_per_mq', 'macrozone']].dropna()

    groups = [
        group['price_per_mq'].values for name, group in anova_data.groupby('macrozone')
    ]

    anova_result = stats.f_oneway(*groups)

    grand_mean = anova_data['price_per_mq'].mean()
    between_variation = sum(
        len(group) * (group['price_per_mq'].mean() - grand_mean) ** 2
        for name, group in anova_data.groupby('macrozone')
    )
    total_variation = sum((anova_data['price_per_mq'] - grand_mean) ** 2)
    eta_squared = between_variation / total_variation

    print('ANOVA - 32 MACROZONES')
    print('F-statistic:', anova_result.statistic)
    print('Degrees of freedom:', len(groups) - 1, ',', len(anova_data) - len(groups))
    print('p-value:', anova_result.pvalue)
    print('Eta squared:', eta_squared)

    return anova_result, eta_squared


def welch_anova(df_clean):

    anova_data = df_clean[['price_per_mq', 'macrozone']].dropna()

    groups = [
        group['price_per_mq'].values for name, group in anova_data.groupby('macrozone')
    ]

    levene_result = stats.levene(*groups)
    welch_result = anova_oneway(
        anova_data['price_per_mq'], groups=anova_data['macrozone'], use_var='unequal'
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

    model = sm.formula.ols('price_per_mq ~ C(macrozone)', data=residual_data).fit()

    fitted_values = model.fittedvalues
    residuals = model.resid

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].scatter(fitted_values, residuals)
    axes[0].axhline(0, linestyle='--')
    axes[0].set_title('Residuals vs Fitted')
    axes[0].set_xlabel('Fitted Values')
    axes[0].set_ylabel('Residuals')

    stats.probplot(residuals, dist='norm', plot=axes[1])
    axes[1].set_title('Q-Q Plot of Residuals')

    plt.tight_layout()
    plt.savefig('charts/anova_residuals.png', dpi=150)
    plt.show()

    return model


def tukey_posthoc(df_clean):

    tukey_data = df_clean[['price_per_mq', 'macrozone']].dropna()

    tukey_result = pairwise_tukeyhsd(
        endog=tukey_data['price_per_mq'], groups=tukey_data['macrozone'], alpha=0.05
    )

    tukey_table = pd.DataFrame(
        data=tukey_result._results_table.data[1:],
        columns=tukey_result._results_table.data[0],
    )

    significant_pairs = tukey_table[tukey_table['reject'] == True]

    print('TUKEY HSD')
    print('Total comparisons:', len(tukey_table))
    print('Significant comparisons:', len(significant_pairs))
    print('\n')
    print('Most significant pairs')

    significant_pairs = significant_pairs.copy()
    significant_pairs['abs_meandiff'] = significant_pairs['meandiff'].abs()
    significant_pairs = significant_pairs.sort_values('abs_meandiff', ascending=False)

    print(
        significant_pairs[['group1', 'group2', 'meandiff', 'p-adj', 'reject']].head(10)
    )

    return tukey_result, significant_pairs


def plot_macrozone_boxplots(df_clean):

    boxplot_data = df_clean[['price_per_mq', 'macrozone']].dropna()

    macrozone_order = (
        boxplot_data.groupby('macrozone')['price_per_mq'].median().sort_values().index
    )

    data = [
        boxplot_data[boxplot_data['macrozone'] == macrozone]['price_per_mq']
        for macrozone in macrozone_order
    ]

    # horizontal, so the 32 zone names read left to right instead of rotated
    # 90 degrees. The names are long, and vertical they cost more height than
    # the plot itself and become unreadable as soon as the figure is scaled.
    plt.figure(figsize=(11, 13))
    plt.boxplot(data, tick_labels=macrozone_order, vert=False)
    plt.title('Price per m² by Macrozone')
    plt.xlabel('Price per m² (€ / m²)')
    plt.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig('charts/macrozone_boxplots.png', dpi=150)
    plt.show()


def anova_phase(df_clean):

    print('\n')
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
    print('\n')


def prepare_correlation_data(df_clean):

    correlation_data = df_clean.copy()

    condition_mapping = {
        'Da ristrutturare': 1,
        'Buono / Abitabile': 2,
        'Ottimo / Ristrutturato': 3,
        'Nuovo / In costruzione': 4,
    }

    correlation_data['condition_numeric'] = correlation_data['condition'].map(
        condition_mapping
    )

    return correlation_data


def correlation_analysis(df_clean):

    correlation_data = prepare_correlation_data(df_clean)

    variables = ['surface_mq', 'rooms', 'bathrooms', 'condition_numeric', 'floor']

    print('CORRELATION WITH PRICE')

    for variable in variables:

        data = correlation_data[[variable, 'price']].dropna()
        pearson = stats.pearsonr(data[variable], data['price'])
        spearman = stats.spearmanr(data[variable], data['price'])

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
        'floor',
    ]

    correlation_matrix = correlation_data[variables].corr(method='pearson')

    print('\n')
    print('CORRELATION MATRIX')
    print(correlation_matrix)

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0)
    plt.title('Correlation Matrix')

    plt.tight_layout()
    plt.savefig('charts/correlation_matrix.png', dpi=150)
    plt.show()

    return correlation_matrix


def pearson_spearman_comparison(df_clean):

    correlation_data = prepare_correlation_data(df_clean)

    variables = ['surface_mq', 'rooms', 'bathrooms', 'condition_numeric', 'floor']

    pearson_values = []
    spearman_values = []

    for variable in variables:

        data = correlation_data[[variable, 'price']].dropna()
        pearson = stats.pearsonr(data[variable], data['price']).statistic
        spearman = stats.spearmanr(data[variable], data['price']).statistic

        pearson_values.append(pearson)
        spearman_values.append(spearman)

    comparison = pd.DataFrame(
        {'variable': variables, 'Pearson': pearson_values, 'Spearman': spearman_values}
    )

    print('\n')
    print('PEARSON VS SPEARMAN')
    print(comparison)

    x = np.arange(len(variables))
    width = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar(x - width / 2, pearson_values, width, label='Pearson')
    plt.bar(x + width / 2, spearman_values, width, label='Spearman')
    plt.axhline(0, linestyle='--')
    plt.xticks(x, variables, rotation=45)
    plt.ylabel('Correlation with Price')
    plt.title('Pearson vs Spearman Correlation')
    plt.legend()

    plt.tight_layout()
    plt.savefig('charts/pearson_spearman_comparison.png', dpi=150)
    plt.show()

    return comparison


def correlation_phase(df_clean):

    print('\n')
    print('PHASE 6 - CORRELATION')
    print('\n')

    correlation_analysis(df_clean)
    print('\n')
    correlation_matrix(df_clean)
    print('\n')
    pearson_spearman_comparison(df_clean)
    print('\n')


def linear_regression(df_clean):

    regression_data = df_clean[['price', 'surface_mq']].dropna()

    X = regression_data['surface_mq']
    X = sm.add_constant(X)
    y = regression_data['price']

    model = sm.OLS(y, X).fit()

    print('LINEAR REGRESSION')
    print('\n')
    print('Intercept:', model.params['const'])
    print('Surface coefficient:', model.params['surface_mq'])
    print('R-squared:', model.rsquared)
    print('Adjusted R-squared:', model.rsquared_adj)
    print('t-statistic:', model.tvalues['surface_mq'])
    print('p-value:', model.pvalues['surface_mq'])
    print('95% confidence interval:')
    print(model.conf_int().loc['surface_mq'])

    return model


def plot_linear_regression(df_clean, model):

    regression_data = df_clean[['price', 'surface_mq']].dropna()

    x = regression_data['surface_mq']
    y = regression_data['price']
    predicted = model.predict(sm.add_constant(x))

    plt.figure(figsize=(9, 8))
    plt.scatter(x, y, alpha=0.3)
    plt.plot(x, predicted, color='red')
    plt.title('Linear Regression: Price vs Surface')
    plt.xlabel('Surface (m²)')
    plt.ylabel('Price (€)')
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('charts/linear_regression.png', dpi=150)
    plt.show()


def linear_residual_diagnostics(model):

    fitted_values = model.fittedvalues
    residuals = model.resid

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].scatter(fitted_values, residuals, alpha=0.3)
    axes[0].axhline(0, linestyle='--')
    axes[0].set_title('Residuals vs Fitted')
    axes[0].set_xlabel('Fitted Values')
    axes[0].set_ylabel('Residuals')

    stats.probplot(residuals, dist='norm', plot=axes[1])
    axes[1].set_title('Q-Q Plot of Residuals')

    plt.tight_layout()
    plt.savefig('charts/linear_regression_residuals.png', dpi=150)
    plt.show()

    return residuals


def breusch_pagan_test(model):

    residuals = model.resid
    exog = model.model.exog

    bp_test = het_breuschpagan(residuals, exog)
    labels = ['LM statistic', 'LM p-value', 'F statistic', 'F p-value']
    results = dict(zip(labels, bp_test))

    print('\n')
    print('BREUSCH-PAGAN TEST')
    print('LM statistic:', results['LM statistic'])
    print('LM p-value:', results['LM p-value'])
    print('F statistic:', results['F statistic'])
    print('F p-value:', results['F p-value'])

    return results


def log_linear_regression(df_clean):

    regression_data = df_clean[['price', 'surface_mq']].dropna()

    regression_data = regression_data[
        (regression_data['price'] > 0) & (regression_data['surface_mq'] > 0)
    ].copy()

    regression_data['log_price'] = np.log(regression_data['price'])
    regression_data['log_surface'] = np.log(regression_data['surface_mq'])

    X = regression_data['log_surface']
    X = sm.add_constant(X)
    y = regression_data['log_price']

    model = sm.OLS(y, X).fit()

    print('\n')
    print('LOG-LOG LINEAR REGRESSION')
    print('\n')
    print('Intercept:', model.params['const'])
    print('Log surface coefficient:', model.params['log_surface'])
    print('R-squared:', model.rsquared)
    print('Adjusted R-squared:', model.rsquared_adj)
    print('t-statistic:', model.tvalues['log_surface'])
    print('p-value:', model.pvalues['log_surface'])
    print('95% confidence interval:')
    print(model.conf_int().loc['log_surface'])

    return model


def log_residual_diagnostics(model):

    fitted_values = model.fittedvalues
    residuals = model.resid

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].scatter(fitted_values, residuals, alpha=0.3)
    axes[0].axhline(0, linestyle='--')
    axes[0].set_title('Log-Log Residuals vs Fitted')
    axes[0].set_xlabel('Fitted Log Price')
    axes[0].set_ylabel('Residuals')

    stats.probplot(residuals, dist='norm', plot=axes[1])
    axes[1].set_title('Q-Q Plot of Log-Log Residuals')

    plt.tight_layout()
    plt.savefig('charts/log_linear_regression_residuals.png', dpi=150)
    plt.show()


def log_breusch_pagan_test(model):

    residuals = model.resid
    exog = model.model.exog

    bp_test = het_breuschpagan(residuals, exog)
    labels = ['LM statistic', 'LM p-value', 'F statistic', 'F p-value']
    results = dict(zip(labels, bp_test))

    print('\n')
    print('BREUSCH-PAGAN TEST - LOG-LOG')
    print('LM statistic:', results['LM statistic'])
    print('LM p-value:', results['LM p-value'])
    print('F statistic:', results['F statistic'])
    print('F p-value:', results['F p-value'])

    return results


def linear_regression_phase(df_clean):

    print('\n')
    print('PHASE 7 - LINEAR REGRESSION')
    print('\n')

    linear_model = linear_regression(df_clean)
    print('\n')
    plot_linear_regression(df_clean, linear_model)
    print('\n')
    linear_residual_diagnostics(linear_model)
    print('\n')
    breusch_pagan_test(linear_model)
    print('\n')

    log_model = log_linear_regression(df_clean)
    print('\n')
    log_residual_diagnostics(log_model)
    print('\n')
    log_breusch_pagan_test(log_model)
    print('\n')

    return linear_model, log_model


def prepare_regression_data(df_clean):

    regression_data = prepare_correlation_data(df_clean)

    regression_data['log_price'] = np.log(regression_data['price'])
    regression_data['log_surface'] = np.log(regression_data['surface_mq'])

    variables = [
        'log_price',
        'log_surface',
        'rooms',
        'bathrooms',
        'condition_numeric',
        'elevator',
        'floor',
        'heating',
        'luxury',
        'macrozone',
    ]

    regression_data = regression_data[variables].dropna()

    print('REGRESSION DATA')
    print('rows before dropna:', len(df_clean))
    print('rows after dropna:', len(regression_data))

    return regression_data


def vif_analysis(regression_data):

    variables = [
        'log_surface',
        'rooms',
        'bathrooms',
        'condition_numeric',
        'elevator',
        'floor',
        'luxury',
    ]

    X = sm.add_constant(regression_data[variables])

    vif = pd.DataFrame(
        {
            'variable': variables,
            'VIF': [
                variance_inflation_factor(X.values, i + 1)
                for i in range(len(variables))
            ],
        }
    )

    print('VIF')
    print(vif.round(2))

    return vif


def multiple_regression(regression_data):

    formula = (
        'log_price ~ log_surface + rooms + bathrooms + condition_numeric'
        ' + elevator + floor + C(heating) + luxury + C(macrozone)'
    )

    model = sm.formula.ols(formula, data=regression_data).fit()

    coefficients = pd.DataFrame({'coefficient': model.params, 'p-value': model.pvalues})
    coefficients = coefficients[~coefficients.index.str.contains('macrozone')]

    print('MULTIPLE LINEAR REGRESSION')
    print('R-squared:', model.rsquared)
    print('Adjusted R-squared:', model.rsquared_adj)
    print('AIC:', model.aic)
    print('\n')
    print(coefficients.round(4))

    return model


def zone_comparison(regression_data):

    formula = (
        'log_price ~ log_surface + rooms + bathrooms + condition_numeric'
        ' + elevator + floor + C(heating) + luxury'
    )

    without_zone = sm.formula.ols(formula, data=regression_data).fit()
    with_zone = sm.formula.ols(formula + ' + C(macrozone)', data=regression_data).fit()

    comparison = pd.DataFrame(
        {
            'coef no zone': without_zone.params,
            'p no zone': without_zone.pvalues,
            'coef with zone': with_zone.params,
            'p with zone': with_zone.pvalues,
        }
    )
    comparison = comparison[~comparison.index.str.contains('macrozone')]

    print('WITH AND WITHOUT ZONE DUMMIES')
    print('Adjusted R-squared without zone:', without_zone.rsquared_adj)
    print('Adjusted R-squared with zone:', with_zone.rsquared_adj)
    print('\n')
    print(comparison.round(4).to_string())

    return comparison


def robust_standard_errors(model):

    robust_model = model.model.fit(cov_type='HC3')

    comparison = pd.DataFrame(
        {
            'OLS std error': model.bse,
            'HC3 std error': robust_model.bse,
            'HC3 p-value': robust_model.pvalues,
        }
    )
    comparison = comparison[~comparison.index.str.contains('macrozone')]

    print('ROBUST STANDARD ERRORS (HC3)')
    print(comparison.round(4))

    return robust_model


def multiple_residual_diagnostics(model):

    fitted_values = model.fittedvalues
    residuals = model.resid

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].scatter(fitted_values, residuals, alpha=0.3)
    axes[0].axhline(0, linestyle='--')
    axes[0].set_title('Multiple Regression Residuals vs Fitted')
    axes[0].set_xlabel('Fitted Log Price')
    axes[0].set_ylabel('Residuals')

    stats.probplot(residuals, dist='norm', plot=axes[1])
    axes[1].set_title('Q-Q Plot of Residuals')

    plt.tight_layout()
    plt.savefig('charts/multiple_regression_residuals.png', dpi=150)
    plt.show()

    return residuals


def model_comparison(regression_data, model):

    log_model = sm.formula.ols('log_price ~ log_surface', data=regression_data).fit()

    comparison = pd.DataFrame(
        {
            'model': ['log-log simple', 'multiple'],
            'Adjusted R-squared': [log_model.rsquared_adj, model.rsquared_adj],
            'AIC': [log_model.aic, model.aic],
        }
    )

    print('MODEL COMPARISON')
    print(comparison.round(4))

    return comparison


def multiple_regression_phase(df_clean):

    print('\n')
    print('PHASE 8 - MULTIPLE LINEAR REGRESSION')
    print('\n')

    regression_data = prepare_regression_data(df_clean)
    print('\n')
    vif_analysis(regression_data)
    print('\n')
    model = multiple_regression(regression_data)
    print('\n')
    zone_comparison(regression_data)
    print('\n')
    robust_standard_errors(model)
    print('\n')
    multiple_residual_diagnostics(model)
    print('\n')
    model_comparison(regression_data, model)
    print('\n')

    return regression_data, model


def conclusions_table(model):

    confidence_intervals = model.conf_int()

    conclusions = pd.DataFrame(
        {
            'coefficient': model.params,
            'CI lower': confidence_intervals[0],
            'CI upper': confidence_intervals[1],
            'p-value': model.pvalues,
        }
    )
    conclusions = conclusions[~conclusions.index.str.contains('macrozone')]
    conclusions = conclusions.drop('Intercept')
    conclusions['significant'] = conclusions['p-value'] < 0.05

    print('PREDICTORS WITH 95% CONFIDENCE INTERVALS')
    print(conclusions.round(4).to_string())

    return conclusions


def zone_variance_share(regression_data, model):

    formula = (
        'log_price ~ log_surface + rooms + bathrooms + condition_numeric'
        ' + elevator + floor + C(heating) + luxury'
    )

    without_zone = sm.formula.ols(formula, data=regression_data).fit()

    print('VARIANCE EXPLAINED BY ZONE')
    print('Adjusted R-squared without zone:', without_zone.rsquared_adj)
    print('Adjusted R-squared with zone:', model.rsquared_adj)
    print('Difference:', model.rsquared_adj - without_zone.rsquared_adj)

    return without_zone


def plot_zone_control(without_zone, model):

    # the two premiums are read as separate bars rather than one bar split in
    # two: the coefficients are multiplicative in log space, so the share the
    # neighbourhood accounts for is not the arithmetic difference of the two
    coefficients = ['luxury', 'elevator']
    labels = ['Luxury segment', 'Lift in the building']

    before = [(np.exp(without_zone.params[name]) - 1) * 100
              for name in coefficients]
    after = [(np.exp(model.params[name]) - 1) * 100 for name in coefficients]

    position = np.arange(len(coefficients))
    height = 0.38

    # the axis is inverted below, so the smaller offset is the upper bar
    plt.figure(figsize=(9, 6.5))
    plt.barh(position - height / 2, before, height, label='without zone')
    plt.barh(position + height / 2, after, height, label='with zone')

    for y, value in zip(position - height / 2, before):
        plt.text(value + 1, y, f'+{value:.1f}%', va='center')

    for y, value in zip(position + height / 2, after):
        plt.text(value + 1, y, f'+{value:.1f}%', va='center')

    plt.yticks(position, labels)
    plt.gca().invert_yaxis()  # the luxury result is the headline: keep it on top
    plt.xlim(0, max(before) * 1.15)
    plt.xlabel('Premium on price (%)')
    plt.title('Premium before and after controlling for zone')
    plt.legend()

    plt.tight_layout()
    plt.savefig('charts/zone_control.png', dpi=150)
    plt.show()


def conclusions_phase(regression_data, model):

    print('\n')
    print('PHASE 9 - STATISTICAL CONCLUSIONS')
    print('\n')

    conclusions = conclusions_table(model)
    print('\n')

    significant = conclusions[conclusions['significant']]
    not_significant = conclusions[~conclusions['significant']]

    print('Significant predictors:', list(significant.index))
    print('Not significant predictors:', list(not_significant.index))
    print('\n')

    without_zone = zone_variance_share(regression_data, model)
    print('\n')

    plot_zone_control(without_zone, model)

    return conclusions


MAP_TEMPLATE = '''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Milan — price per m² by zone</title>
<style>
  /* one dark ground for both views: white block edges are what separates one
     zone from the next, and on a light ground they were invisible */
  :root{
    --bg:#111311; --panel:#1a1c1a; --panel-2:#232622; --ink:#f2f3ef;
    --ink-2:#a6aaa2; --ink-3:#7b8078; --line:#2c2f2b; --line-2:#3c403b;
    --accent:#f0783f;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden}
  body{background:var(--bg);color:var(--ink);
       font:14px/1.45 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif}
  #map{position:absolute;inset:0}
  .card{position:absolute;background:var(--panel);border:1px solid var(--line);
        border-radius:9px;box-shadow:0 2px 10px rgba(0,0,0,.45);z-index:2}
  /* a single panel: two separate cards could overlap on short viewports */
  #panel{top:20px;left:20px;width:328px;padding:15px 17px;
         max-height:calc(100vh - 40px);overflow-y:auto}
  #panel h1{margin:0 0 5px;font-size:17px;font-weight:600;letter-spacing:-.2px}
  #panel p{margin:0;font-size:12.5px;color:var(--ink-2)}
  .sec{margin-top:13px;padding-top:12px;border-top:1px solid var(--line)}
  .lab{font-size:11px;text-transform:uppercase;letter-spacing:.07em;
       color:var(--ink-3);margin-bottom:8px}
  #panel dl{display:grid;grid-template-columns:1fr auto;gap:3px 14px;margin:0;
            font-size:12.5px}
  #panel dt{color:var(--ink-2)}
  #panel dd{margin:0;text-align:right;font-variant-numeric:tabular-nums}
  .lg-r{display:flex;align-items:center;gap:10px;padding:2px 0;
        font-size:12.5px;font-variant-numeric:tabular-nums}
  .sw{width:15px;height:15px;border-radius:3px;flex:none;
      border:1px solid var(--line-2)}
  .note{margin:10px 0 0;font-size:11.5px;line-height:1.5;color:var(--ink-2)}
  .btn{width:100%;padding:8px 12px;font:inherit;font-size:12.5px;
       color:var(--ink);background:var(--panel-2);border:1px solid var(--line);
       border-radius:7px;cursor:pointer}
  .btn:hover{border-color:var(--line-2)}
  .btn[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);
                            color:#fff}
  .switch{display:flex;gap:6px}
  .switch .btn{padding:7px 8px;font-size:12px}
  .list{max-height:232px;overflow-y:auto;margin:0 -6px 0 0;padding-right:6px}
  .zr{display:grid;grid-template-columns:15px 1fr auto;gap:9px;align-items:center;
      width:100%;padding:4px 3px;border:0;border-radius:5px;background:none;
      font:inherit;font-size:12.5px;text-align:left;cursor:pointer;color:var(--ink)}
  .zr:hover{background:var(--panel-2)}
  .zr[aria-current="true"]{background:var(--panel-2);
                           box-shadow:inset 2px 0 0 var(--accent)}
  .zr .nm{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .zr .v{color:var(--ink-2);font-variant-numeric:tabular-nums}
  #compass{right:20px;bottom:20px;width:86px;padding:9px 8px 7px;
           border:1px solid var(--line);cursor:pointer;font:inherit;
           background:var(--panel)}
  #compass:hover{border-color:var(--line-2)}
  #compass svg{width:62px;height:62px;display:block;margin:0 auto}
  #compass circle{stroke:var(--line-2)}
  .n-half,.n-lab{fill:var(--accent)}
  .s-half{fill:var(--ink-3)}
  .rose-lab{fill:var(--ink-2)}
  #spin-sec[hidden]{display:none}
  #compass .deg{margin-top:4px;font-size:11px;color:var(--ink-2);
                text-align:center;font-variant-numeric:tabular-nums}
  /* phones: the panel is an overlay, and on a narrow screen an overlay
     stretched from edge to edge simply covers the map. Map and panel are
     stacked into two bands instead, so neither can hide the other.
     dvh, not vh: on iOS vh counts the area behind the browser chrome. */
  @media(max-width:820px){
    body{display:flex;flex-direction:column;height:100vh;height:100dvh}
    #map{position:relative;inset:auto;flex:1 1 auto;min-height:200px}
    #panel{position:relative;top:auto;left:auto;right:auto;width:auto;
           flex:0 1 auto;min-height:0;max-height:48vh;max-height:48dvh;
           border-radius:0;border-width:1px 0 0;box-shadow:none;
           overscroll-behavior:contain}
    /* one scroll, not a scrollable list inside a scrollable panel */
    .list{max-height:none}
    #compass{display:none}
  }
  /* phone held sideways: a horizontal band would leave the map a sliver */
  @media(max-width:820px) and (orientation:landscape){
    body{flex-direction:row}
    #panel{flex:0 0 292px;max-height:none;border-width:0 0 0 1px}
  }
</style>
</head>
<body>

<div id="map"></div>

<div id="panel" class="card">
  <h1>Milan, price and floor area by zone</h1>
  <p><b>Height</b>: mean price per m². <b>Colour</b>: mean flat floor area.
     Two different variables, over the 88 official city zones (NIL,
     <i>Nuclei d'Identità Locale</i>).</p>

  <div class="sec">
    <dl>
      <dt>Listings mapped</dt><dd id="s-listings"></dd>
      <dt>Zones shown</dt><dd id="s-zones"></dd>
      <dt>City mean price</dt><dd id="s-mean"></dd>
      <dt>City mean floor area</dt><dd id="s-surface"></dd>
    </dl>
  </div>

  <div class="sec">
    <div class="lab">View</div>
    <div class="switch">
      <button class="btn" type="button" data-view="3d" aria-pressed="true">
        3D</button>
      <button class="btn" type="button" data-view="2d" aria-pressed="false">
        2D flat</button>
    </div>
    <p class="note" id="view-note"></p>
  </div>

  <div class="sec">
    <div class="lab" id="mode-lab"></div>
    <div class="switch">
      <button class="btn" type="button" data-mode="avg" aria-pressed="true">
        Mean price</button>
      <button class="btn" type="button" data-mode="premium" aria-pressed="false">
        Reference flat</button>
    </div>
    <p class="note" id="mode-note"></p>
  </div>

  <div class="sec">
    <div class="lab" id="lg-lab"></div>
    <div id="lg-rows"></div>
    <p class="note" id="lg-note"></p>
  </div>

  <div class="sec">
    <div class="lab" id="list-lab"></div>
    <div id="zone-list" class="list"></div>
    <p class="note">Click a zone here or straight on the map. Click away from
       the zones, or press Esc, to go back to the overview.</p>
  </div>

  <div class="sec" id="spin-sec">
    <button id="spin" class="btn" type="button" aria-pressed="false">Spin 360°</button>
    <p class="note">Drag to turn the map by hand, scroll to zoom, hover a zone
       for its figures. The compass at the bottom right puts north back up.</p>
  </div>
</div>

<button id="compass" class="card" type="button" title="Put north back up"
        aria-label="Compass: click to put north back up">
  <svg viewBox="0 0 100 100" aria-hidden="true">
    <circle cx="50" cy="50" r="47" fill="none" stroke-width="2"/>
    <g id="rose" font-size="17" text-anchor="middle" dominant-baseline="central">
      <polygon points="50,26 57,50 43,50" class="n-half"/>
      <polygon points="50,74 57,50 43,50" class="s-half"/>
      <text x="50" y="11" class="n-lab" font-weight="600">N</text>
      <text x="89" y="50" class="rose-lab">E</text>
      <text x="50" y="89" class="rose-lab">S</text>
      <text x="11" y="50" class="rose-lab">W</text>
    </g>
  </svg>
  <div class="deg" id="cp-deg"></div>
</button>

<script>/*LIBRARY*/</script>
<script type="application/json" id="Z">/*GEOJSON*/</script>
<script type="application/json" id="M">/*METADATA*/</script>
<script>
var D = JSON.parse(document.getElementById('Z').textContent);
var M = JSON.parse(document.getElementById('M').textContent);

// sequential single hue, darker as the value grows. The orange is stepped for
// the dark ground of the 3D view, where #a05520 is as dark as a class can get
// before it sinks into the background; the blue is stepped for the light
// ground of the flat view.
var SURFACE = [
  [248, 202, 151],
  [237, 168, 98],
  [221, 134, 54],
  [194, 106, 36],
  [160, 85, 32]
];
var PRICE = [
  [205, 226, 251],
  [158, 197, 244],
  [109, 167, 236],
  [57, 135, 229],
  [37, 106, 191]
];
var NODATA = [74, 77, 71];

function fmt(value) {
  return value == null ? 'n/a' : value.toLocaleString('en-GB');
}

// 'avg' is the price actually asked in the zone, 'premium' the price of one
// identical flat priced in every zone — the second isolates the location
var mode = 'avg';
var view = '3d';
var selected = null;

function height(properties) {
  return mode === 'avg' ? properties.avg : properties.premium;
}

function outline(feature) {
  return feature.properties.id_nil === selected
    ? [240, 120, 63]
    : [255, 255, 255, 190];
}

function classOf(value, breaks) {
  var index = 0;

  while (index < breaks.length && value >= breaks[index]) {
    index += 1;
  }

  return index;
}

// in 3D the colour is the mean surface, because the height already carries the
// price. Flat there is no height left, so the colour takes the price over.
function ramp() {
  return view === '3d' ? SURFACE : PRICE;
}

function breaks() {
  return view === '3d' ? M.breaks.surface : M.breaks[mode];
}

function baseColor(properties) {
  if (view === '3d') {
    return properties.cls == null ? NODATA : SURFACE[properties.cls];
  }

  var value = height(properties);

  return value == null ? NODATA : PRICE[classOf(value, M.breaks[mode])];
}

// everything but the selected zone fades back, so the selected one reads
// even through the blocks standing in front of it
function fill(feature) {
  var properties = feature.properties;
  var base = baseColor(properties);

  if (selected == null || properties.id_nil === selected) {
    return base;
  }

  return [base[0], base[1], base[2], 105];
}

// focus: with a zone selected the others drop to a third of their height, so
// nothing can stand in front of it whatever the angle. It is a temporary view
// state, and the selected zone keeps its true height.
function elevation(feature) {
  var properties = feature.properties;
  var tall = height(properties) || 0;

  if (selected != null && properties.id_nil !== selected) {
    return tall * 0.33;
  }

  return tall;
}

function tooltip(info) {
  if (!info.object) {
    return null;
  }

  var p = info.object.properties;
  var body;

  if (p.avg == null) {
    body =
      '<div style="font-size:16px">not enough data</div>' +
      '<div style="color:#a6aaa2;font-size:12px;margin-top:3px">' +
      p.n + ' listings</div>';
  } else {
    body =
      '<div style="font-size:19px;letter-spacing:-.3px">' +
      fmt(p.avg) + ' €/m² <span style="font-size:12px;color:#a6aaa2">mean' +
      '</span></div>' +
      '<div style="font-size:19px;letter-spacing:-.3px">' +
      fmt(p.surface_avg) + ' m² <span style="font-size:12px;color:#a6aaa2">' +
      'mean</span></div>' +
      '<div style="color:#a6aaa2;font-size:12px;margin-top:5px">' +
      'reference flat ' + fmt(p.premium) + ' €/m²</div>' +
      '<div style="color:#a6aaa2;font-size:12px">' +
      'median ' + fmt(p.med) + ' €/m² · p25–p75 ' +
      fmt(p.p25) + '–' + fmt(p.p75) + '</div>' +
      '<div style="color:#a6aaa2;font-size:12px">' +
      p.n + ' listings · median price ' + fmt(p.mp) + ' € · ' +
      'median floor area ' + fmt(p.surface_med) + ' m²</div>';
  }

  return {
    html: '<div style="font-weight:600;margin-bottom:4px">' + p.nome +
          '</div>' + body,
    style: {
      background: '#1a1c1a',
      color: '#f2f3ef',
      border: '1px solid #3c403b',
      borderRadius: '8px',
      padding: '11px 13px',
      boxShadow: '0 4px 16px rgba(0,0,0,.5)',
      font: '13px/1.45 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif',
      maxWidth: '280px'
    }
  };
}

function makeLayer() {
  return new deck.GeoJsonLayer({
    id: 'zones',
    data: D,
    extruded: view === '3d',
    filled: true,
    wireframe: true,
    stroked: view === '2d',
    lineWidthMinPixels: 1,
    getElevation: elevation,
    elevationScale: M.elevation_scale,
    getFillColor: fill,
    getLineColor: outline,
    pickable: true,
    autoHighlight: true,
    highlightColor: [240, 120, 63, 130],
    updateTriggers: {
      getElevation: [mode, selected, view],
      getLineColor: selected,
      getFillColor: [selected, view, mode]
    }
  });
}

// a floating label on top of the selected block: the outline alone does not
// say which zone one is looking at
function makeLabel() {
  if (selected == null) {
    return null;
  }

  var chosen = D.features.filter(function (feature) {
    return feature.properties.id_nil === selected;
  });

  if (!chosen.length) {
    return null;
  }

  return new deck.TextLayer({
    id: 'label',
    data: [chosen[0].properties],
    getPosition: function (p) {
      var lift = view === '3d' ? (height(p) || 0) * M.elevation_scale : 0;

      return [p.lon, p.lat, lift];
    },
    getText: function (p) {
      return p.nome + ' · ' + fmt(height(p)) + ' €/m²';
    },
    getSize: 13,
    getColor: [242, 243, 239],
    getPixelOffset: [0, -16],
    billboard: true,
    background: true,
    getBackgroundColor: [26, 28, 26, 240],
    backgroundPadding: [8, 5, 8, 5],
    getBorderColor: [240, 120, 63],
    getBorderWidth: 1.5,
    fontFamily: 'ui-sans-serif, -apple-system, "Segoe UI", Roboto, sans-serif',
    characterSet: 'auto'
  });
}

function refresh() {
  deckgl.setProps({layers: [makeLayer(), makeLabel()].filter(Boolean)});
}

var rose = document.getElementById('rose');
var degrees = document.getElementById('cp-deg');

// the zoom levels below are chosen for a desktop window. Milan is about 0.24°
// of longitude across, which at zoom 10.7 needs some 570px: on a phone the
// city would simply run off both sides. Cap every zoom to what fits instead.
var CITY_SPAN_LON = 0.28; // degrees, the city plus a margin

function fitZoom(preferred) {
  var fits = Math.log2(360 * window.innerWidth / (512 * CITY_SPAN_LON));
  return Math.min(preferred, fits);
}

// zooming out past the city is never useful: there is no basemap under the
// zones, so it would only shrink Milan into an empty screen. On a narrow
// screen the floor has to go below 10, or it would clamp the fitted zoom.
var MIN_ZOOM = Math.min(10, fitZoom(10.7));

var viewState = {
  longitude: 9.19,
  latitude: 45.44,
  zoom: fitZoom(10.7),
  pitch: 50,
  bearing: -20,
  minZoom: MIN_ZOOM
};

// the compass rose turns against the bearing, so its needle keeps pointing
// at the real north whatever the camera is doing
function applyViewState(next) {
  // reapplied every time so the limit cannot be dropped by a state coming
  // back from the controller
  viewState = Object.assign({}, next, {minZoom: MIN_ZOOM});
  deckgl.setProps({viewState: viewState});

  var bearing = viewState.bearing || 0;

  rose.setAttribute('transform', 'rotate(' + -bearing + ' 50 50)');
  degrees.textContent = Math.round((bearing % 360 + 360) % 360) + '°';
}

var deckgl = new deck.DeckGL({
  container: document.getElementById('map'),
  viewState: viewState,
  controller: true,
  layers: [makeLayer()],
  getTooltip: tooltip,
  onClick: function (info) {
    if (info.object) {
      selectZone(info.object.properties);
    } else if (selected != null) {
      clearSelection();
    }
  },
  onViewStateChange: function (event) {
    var interaction = event.interactionState || {};

    if (interaction.isDragging || interaction.isZooming) {
      stopSpin();
    }

    applyViewState(event.viewState);
  }
});

applyViewState(viewState);

// camera moves are animated by hand rather than with a deck.gl transition:
// the view state is controlled, and a controlled update on every frame would
// cancel the transition halfway
var move = null;

function moveStep(time) {
  if (!move) {
    return;
  }

  if (!move.start) {
    move.start = time;
  }

  var step = Math.min((time - move.start) / move.duration, 1);
  var eased = step * (2 - step);
  var next = Object.assign({}, viewState);

  for (var key in move.target) {
    next[key] = move.from[key] + (move.target[key] - move.from[key]) * eased;
  }

  applyViewState(next);

  if (step < 1) {
    requestAnimationFrame(moveStep);
  } else {
    move = null;
  }
}

function animateTo(target, duration) {
  stopSpin();
  move = {from: viewState, target: target, duration: duration, start: 0};
  requestAnimationFrame(moveStep);
}

document.getElementById('compass').addEventListener('click', function () {
  // shortest way round: bring the bearing back into -180..180 first
  var bearing = ((viewState.bearing % 360) + 540) % 360 - 180;

  applyViewState(Object.assign({}, viewState, {bearing: bearing}));
  animateTo({bearing: 0}, 500);
});

// full turn every 36 seconds, driven by elapsed time so the speed does not
// depend on the frame rate
var button = document.getElementById('spin');
var spinning = false;
var lastFrame = 0;

function spin(time) {
  if (!spinning) {
    return;
  }

  if (lastFrame) {
    var bearing = viewState.bearing + (time - lastFrame) * 0.01;

    applyViewState(Object.assign({}, viewState, {bearing: bearing % 360}));
  }

  lastFrame = time;
  requestAnimationFrame(spin);
}

// stops every automatic camera motion, so the user taking over always wins
function stopSpin() {
  spinning = false;
  move = null;
  lastFrame = 0;
  button.textContent = 'Spin 360°';
  button.setAttribute('aria-pressed', 'false');
}

button.addEventListener('click', function () {
  if (spinning) {
    stopSpin();
    return;
  }

  stopSpin();
  spinning = true;
  lastFrame = 0;
  button.textContent = 'Stop spinning';
  button.setAttribute('aria-pressed', 'true');
  requestAnimationFrame(spin);
});

function legendRow(color, label) {
  return '<div class="lg-r"><span class="sw" style="background:rgb(' +
         color.join(',') + ')"></span>' + label + '</div>';
}

document.getElementById('s-listings').textContent = fmt(M.listings);
document.getElementById('s-zones').textContent = M.zones + ' of 88';
document.getElementById('s-mean').textContent = fmt(M.mean) + ' €/m²';
document.getElementById('s-surface').textContent = M.surface_mean + ' m²';

function buildLegend() {
  var cuts = breaks();
  var colors = ramp();
  var labels = [
    'up to ' + fmt(cuts[0]),
    fmt(cuts[0]) + ' – ' + fmt(cuts[1]),
    fmt(cuts[1]) + ' – ' + fmt(cuts[2]),
    fmt(cuts[2]) + ' – ' + fmt(cuts[3]),
    'over ' + fmt(cuts[3])
  ];

  var rows = '';

  for (var i = labels.length - 1; i >= 0; i--) {
    rows += legendRow(colors[i], labels[i]);
  }

  rows += legendRow(NODATA, 'fewer than ' + M.min_listings + ' listings');

  document.getElementById('lg-rows').innerHTML = rows;
  document.getElementById('lg-lab').textContent =
    view === '3d'
      ? 'Colour — mean floor area m²'
      : 'Colour — ' +
        (mode === 'avg' ? 'mean price' : 'reference flat') + ' €/m²';

  document.getElementById('lg-note').textContent =
    view === '3d'
      ? 'In 3D the colour is not the price: it is the mean floor area, ' +
        'because the height already carries the price (proportional from ' +
        'zero, scale ' + M.elevation_scale + ').'
      : 'With no height left, the colour takes the price over. Mean floor ' +
        'area stays in the tooltip.';
}

// the ranked list is the honest counterpart of the height: in perspective the
// blocks cannot be compared by eye, and the tall ones hide the short ones
var list = document.getElementById('zone-list');
var listLabel = document.getElementById('list-lab');
var modeNote = document.getElementById('mode-note');
var modeButtons = document.querySelectorAll('[data-mode]');

function buildList() {
  var zones = D.features
    .map(function (feature) {
      return feature.properties;
    })
    .filter(function (p) {
      return height(p) != null;
    })
    .sort(function (a, b) {
      return height(b) - height(a);
    });

  var html = '';

  zones.forEach(function (p, index) {
    html +=
      '<button class="zr" type="button" data-id="' + p.id_nil +
      '" data-lon="' + p.lon + '" data-lat="' + p.lat + '"' +
      (p.id_nil === selected ? ' aria-current="true"' : '') + '>' +
      '<span class="sw" style="background:rgb(' +
      baseColor(p).join(',') + ')"></span>' +
      '<span class="nm">' + (index + 1) + '. ' + p.nome + '</span>' +
      '<span class="v">' + fmt(height(p)) + '</span></button>';
  });

  list.innerHTML = html;
  listLabel.textContent =
    'Zones by ' + (mode === 'avg' ? 'mean price' : 'reference flat') +
    ' — ' + zones.length + ' of 88';
}

// with a tilted camera the blocks between the viewer and the target hide it,
// so the map turns to the side with the least tall mass in the way. The
// viewer stands opposite the screen-up direction, at bearing + 180.
function clearestBearing(lon, lat) {
  var best = 0;
  var bestScore = Infinity;

  for (var bearing = 0; bearing < 360; bearing += 15) {
    var angle = ((bearing + 180) * Math.PI) / 180;
    var east = Math.sin(angle);
    var north = Math.cos(angle);
    var score = 0;

    D.features.forEach(function (feature) {
      var p = feature.properties;
      var tall = height(p);

      if (!tall || p.id_nil === selected) {
        return;
      }

      // rough km: one degree of longitude is about 78 km at this latitude
      var dx = (p.lon - lon) * 78;
      var dy = (p.lat - lat) * 111;
      var distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < 0.25 || distance > 6) {
        return;
      }

      var aligned = (dx * east + dy * north) / distance;

      // only what stands in front can hide, and the nearer it is the worse
      if (aligned > 0) {
        score += (tall * Math.pow(aligned, 4)) / distance;
      }
    });

    if (score < bestScore) {
      bestScore = score;
      best = bearing;
    }
  }

  return best;
}

function markRow() {
  var current = list.querySelector('[aria-current="true"]');

  if (current) {
    current.removeAttribute('aria-current');
  }

  if (selected == null) {
    return;
  }

  var row = list.querySelector('[data-id="' + selected + '"]');

  if (row) {
    row.setAttribute('aria-current', 'true');

    if (row.scrollIntoView) {
      row.scrollIntoView({block: 'nearest'});
    }
  }
}

function selectZone(properties) {
  selected = properties.id_nil;
  refresh();
  markRow();

  var lon = properties.lon;
  var lat = properties.lat;

  // shortest way round to the bearing that leaves the zone in the clear
  var wanted = view === '3d' ? clearestBearing(lon, lat) : 0;
  var turn = (((wanted - viewState.bearing) % 360) + 540) % 360 - 180;

  animateTo(
    {
      longitude: lon,
      latitude: lat,
      zoom: 12.2,
      bearing: viewState.bearing + turn,
      pitch: view === '3d' ? 40 : 0
    },
    900
  );
}

function clearSelection() {
  selected = null;
  refresh();
  markRow();

  animateTo(
    {
      longitude: 9.19,
      latitude: view === '3d' ? 45.44 : 45.46,
      zoom: fitZoom(view === '3d' ? 10.7 : 11.2),
      bearing: 0,
      pitch: view === '3d' ? 50 : 0
    },
    800
  );
}

function zoneById(id) {
  var found = D.features.filter(function (feature) {
    return feature.properties.id_nil === id;
  });

  return found.length ? found[0].properties : null;
}

list.addEventListener('click', function (event) {
  var row = event.target.closest('.zr');

  if (row) {
    selectZone(zoneById(Number(row.dataset.id)));
  }
});

document.addEventListener('keydown', function (event) {
  if (event.key === 'Escape' && selected != null) {
    clearSelection();
  }
});

var R = M.reference;

function setMode(next) {
  mode = next;

  Array.prototype.forEach.call(modeButtons, function (item) {
    item.setAttribute('aria-pressed', String(item.dataset.mode === mode));
  });

  refresh();
  buildList();
  buildLegend();

  document.getElementById('mode-lab').textContent =
    view === '3d' ? 'Block height' : 'Variable shown';

  modeNote.textContent =
    mode === 'avg'
      ? 'The price actually asked in the zone. It carries the fact that in some ' +
        'neighbourhoods the flats are larger and better kept than elsewhere.'
      : 'What the same flat — ' + R.surface + ' m², ' + R.rooms + ' rooms, ' +
        R.bathrooms + ' bathroom, renovated, floor ' + R.floor + ' with a lift ' +
        '— would cost in that zone. It separates the location from the ' +
        'properties that happen to stand on it. Estimated over ' +
        M.premium_zones + ' zones.';
}

Array.prototype.forEach.call(modeButtons, function (item) {
  item.addEventListener('click', function () {
    setMode(item.dataset.mode);
  });
});

var viewButtons = document.querySelectorAll('[data-view]');

function setView(next, animate) {
  view = next;

  Array.prototype.forEach.call(viewButtons, function (item) {
    item.setAttribute('aria-pressed', String(item.dataset.view === view));
  });

  document.getElementById('spin-sec').hidden = view === '2d';
  document.getElementById('view-note').textContent =
    view === '3d'
      ? 'Two variables at once, height and colour. Good to look at, but ' +
        'heights seen in perspective cannot be compared by eye.'
      : 'One variable, read from above. Less striking and more precise: no ' +
        'zone can hide another.';

  if (animate) {
    stopSpin();

    if (view === '2d') {
      animateTo({pitch: 0, bearing: 0, zoom: fitZoom(11.2)}, 700);
    } else {
      animateTo({pitch: 45, zoom: fitZoom(10.9)}, 700);
    }
  }

  setMode(mode);
}

Array.prototype.forEach.call(viewButtons, function (item) {
  item.addEventListener('click', function () {
    setView(item.dataset.view, true);
  });
});

setView('3d', false);
</script>

</body>
</html>
'''


def prepare_map_data(df_clean):

    map_data = df_clean[df_clean['nil_id'].notna()]

    print('MAP DATA')
    print('rows before geo filter:', len(df_clean))
    print('rows after geo filter:', len(map_data))
    print('rows without zone:', len(df_clean) - len(map_data))

    return map_data


def zone_aggregates(map_data):

    price_per_mq = map_data.groupby('nil_id')['price_per_mq']
    surface = map_data.groupby('nil_id')['surface_mq']

    zone_stats = pd.DataFrame(
        {
            'n': price_per_mq.size(),
            'avg': price_per_mq.mean(),
            'med': price_per_mq.median(),
            'p25': price_per_mq.quantile(0.25),
            'p75': price_per_mq.quantile(0.75),
            'mp': map_data.groupby('nil_id')['price'].median(),
            'surface_avg': surface.mean(),
            'surface_med': surface.median(),
        }
    )

    zone_stats = zone_stats.round(0).astype(int)
    zone_stats.index = zone_stats.index.astype(int)

    print('ZONE AGGREGATES')
    print('zones with listings:', len(zone_stats))
    print('smallest zone:', zone_stats['n'].min(), 'listings')
    print('largest zone:', zone_stats['n'].max(), 'listings')
    print('\n')
    print('most expensive zones by mean price per sqm:')
    print(zone_stats.sort_values('avg', ascending=False).head(5))

    return zone_stats


def suppress_small_zones(zone_stats, min_listings):

    zone_stats['suppressed'] = zone_stats['n'] < min_listings

    suppressed = zone_stats[zone_stats['suppressed']]

    print('SMALL ZONES SUPPRESSED')
    print('minimum listings:', min_listings)
    print('zones suppressed:', len(suppressed))
    print('zones displayed:', len(zone_stats) - len(suppressed))
    print('\n')
    print(suppressed[['n', 'med']])

    return zone_stats


def value_classes(values, label):

    values = values.dropna()

    quantiles = values.quantile([0.2, 0.4, 0.6, 0.8])
    breaks = [int(quantile) for quantile in quantiles]

    print('COLOR CLASSES -', label)
    print('breaks:', breaks)

    classes = np.searchsorted(breaks, values, side='right')

    for index in range(5):
        print('class', index, '- zones:', (classes == index).sum())

    return breaks


def location_premium(map_data, min_listings):

    premium_data = prepare_correlation_data(map_data)

    premium_data['log_price'] = np.log(premium_data['price'])
    premium_data['log_surface'] = np.log(premium_data['surface_mq'])

    variables = [
        'log_price',
        'log_surface',
        'surface_mq',
        'rooms',
        'bathrooms',
        'condition_numeric',
        'elevator',
        'floor',
        'heating',
        'luxury',
        'nil_id',
    ]

    premium_data = premium_data[variables].dropna()

    counts = premium_data.groupby('nil_id').size()
    kept = counts[counts >= min_listings].index
    premium_data = premium_data[premium_data['nil_id'].isin(kept)]

    formula = (
        'log_price ~ log_surface + rooms + bathrooms + condition_numeric'
        ' + elevator + floor + C(heating) + luxury + C(nil_id)'
    )

    model = sm.formula.ols(formula, data=premium_data).fit()

    # the same flat priced in every zone: the median listing of the city, so
    # what is left is the zone and not the flats that happen to be in it
    reference = {
        'surface_mq': premium_data['surface_mq'].median(),
        'rooms': premium_data['rooms'].median(),
        'bathrooms': premium_data['bathrooms'].median(),
        'condition_numeric': premium_data['condition_numeric'].median(),
        'elevator': premium_data['elevator'].median(),
        'floor': premium_data['floor'].median(),
        'heating': premium_data['heating'].mode()[0],
        'luxury': 0,
    }

    predictors = dict(reference)
    predictors['log_surface'] = np.log(reference['surface_mq'])

    zones = sorted(premium_data['nil_id'].unique())
    grid = pd.DataFrame([dict(predictors, nil_id=zone) for zone in zones])

    # exp of a log-linear prediction estimates the median, not the mean
    premium = np.exp(model.predict(grid)) / reference['surface_mq']
    premium = pd.Series(premium.values, index=[int(zone) for zone in zones])
    premium = premium.round(0).astype(int)

    print('LOCATION PREMIUM')
    print('rows:', len(premium_data))
    print('zones estimated:', len(premium))
    print('adjusted R-squared:', model.rsquared_adj)
    print('\n')

    print('reference flat:')
    for key, value in reference.items():
        print(key + ':', value)
    print('\n')

    print('price per sqm - min:', premium.min(), 'max:', premium.max())
    print('most expensive zones:')
    print(premium.sort_values(ascending=False).head(5))

    return premium, reference


def build_zone_geojson(zone_stats, breaks):

    with open('milano_zone_NIL.geojson', encoding='utf-8') as geojson_file:
        geojson = json.load(geojson_file)

    values = ['avg', 'med', 'p25', 'p75', 'mp', 'surface_avg', 'surface_med']

    for feature in geojson['features']:

        zone_id = feature['properties']['id_nil']

        properties = {
            'id_nil': zone_id,
            'nome': feature['properties']['nome'],
            'lon': feature['properties']['lon_centro'],
            'lat': feature['properties']['lat_centro'],
            'n': 0,
            'cls': None,
            'premium': None,
        }

        for value in values:
            properties[value] = None

        if zone_id in zone_stats.index:

            zone = zone_stats.loc[zone_id]
            properties['n'] = int(zone['n'])

            if not zone['suppressed']:

                for value in values:
                    properties[value] = int(zone[value])

                properties['cls'] = int(
                    np.searchsorted(breaks, zone['surface_avg'], side='right')
                )

                if pd.notna(zone['premium']):
                    properties['premium'] = int(zone['premium'])

        feature['properties'] = properties

    coloured = [f for f in geojson['features'] if f['properties']['cls'] is not None]
    priced = [f for f in geojson['features'] if f['properties']['premium'] is not None]

    print('ZONE GEOJSON')
    print('features:', len(geojson['features']))
    print('features with data:', len(coloured))
    print('features without data:', len(geojson['features']) - len(coloured))
    print('features with a location premium:', len(priced))

    return geojson


def map_metadata(map_data, zone_stats, reference, breaks, min_listings, scale):

    displayed = zone_stats[~zone_stats['suppressed']]

    metadata = {
        'listings': len(map_data),
        'mean': int(map_data['price_per_mq'].mean()),
        'median': int(map_data['price_per_mq'].median()),
        'surface_mean': int(map_data['surface_mq'].mean()),
        'zones': len(displayed),
        'suppressed': int(zone_stats['suppressed'].sum()),
        'premium_zones': int(displayed['premium'].notna().sum()),
        'max_height': int(displayed['avg'].max() * scale),
        'reference': {
            'surface': int(reference['surface_mq']),
            'rooms': int(reference['rooms']),
            'bathrooms': int(reference['bathrooms']),
            'condition': int(reference['condition_numeric']),
            'floor': int(reference['floor']),
            'elevator': int(reference['elevator']),
        },
        'breaks': breaks,
        'min_listings': min_listings,
        'elevation_scale': scale,
        'max_height_premium': int(displayed['premium'].max() * scale),
    }

    print('MAP METADATA')

    for key, value in metadata.items():
        print(key + ':', value)

    return metadata


def write_3d_map(zone_geojson, metadata):

    with open('deck.min.js', encoding='utf-8') as library_file:
        library = library_file.read()

    html = MAP_TEMPLATE
    html = html.replace('/*GEOJSON*/', json.dumps(zone_geojson))
    html = html.replace('/*METADATA*/', json.dumps(metadata))
    html = html.replace('/*LIBRARY*/', library)

    with open('milano-3d.html', 'w', encoding='utf-8') as map_file:
        map_file.write(html)

    print('3D MAP WRITTEN')
    print('file: milano-3d.html')
    print('size MB:', round(len(html) / 1024 / 1024, 2))


def map_phase(df_clean):

    print('\n')
    print('PHASE 10 - 3D MAP BY ZONE')
    print('\n')

    min_listings = 10
    elevation_scale = 0.3

    map_data = prepare_map_data(df_clean)
    print('\n')

    zone_stats = zone_aggregates(map_data)
    print('\n')

    zone_stats = suppress_small_zones(zone_stats, min_listings)
    print('\n')

    premium, reference = location_premium(map_data, min_listings)
    zone_stats['premium'] = premium
    print('\n')

    displayed = zone_stats[~zone_stats['suppressed']]

    breaks = {
        'surface': value_classes(displayed['surface_avg'], 'mean surface in sqm'),
        'avg': value_classes(displayed['avg'], 'mean price per sqm'),
        'premium': value_classes(displayed['premium'], 'reference flat per sqm'),
    }
    print('\n')

    zone_geojson = build_zone_geojson(zone_stats, breaks['surface'])
    print('\n')

    metadata = map_metadata(
        map_data, zone_stats, reference, breaks, min_listings, elevation_scale
    )
    print('\n')

    write_3d_map(zone_geojson, metadata)
    print('\n')

    return zone_stats


# main program

# data cleaning
df_clean = data_cleaning_phase(df_raw)

# PHASE 1 - DESCRIPTIVE STATISTICS
descriptive_statistics_phase(df_clean)

# PHASE 2 — PROBABILITY & DISTRIBUTIONS
distribution_phase(df_clean)

# PHASE 3 - SAMPLING & CONFIDENCE INTERVALS
sampling_phase(df_clean)

# PHASE 4 - HYPOTHESIS TESTING
hypothesis_testing_phase(df_clean)

# PHASE 5 - ANOVA
anova_phase(df_clean)

# PHASE 6 - CORRELATION
correlation_phase(df_clean)

# PHASE 7 - LINEAR REGRESSION
linear_regression_phase(df_clean)

# PHASE 8 - MULTIPLE LINEAR REGRESSION
regression_data, model = multiple_regression_phase(df_clean)

# PHASE 9 - STATISTICAL CONCLUSIONS
conclusions_phase(regression_data, model)

# PHASE 10 - 3D MAP BY ZONE
map_phase(df_clean)
