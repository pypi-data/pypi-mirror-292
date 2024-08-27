import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

def analyze_categorical_feature(df, feature, target="Transported"):
    """
    Analyze a categorical feature in the context of the target variable.
    Parameters:
    df (pd.DataFrame): The dataframe containing the data.
    feature (str): The name of the categorical feature to analyze.
    target (str): The target variable for analysis. Default is "Transported".
    Returns:
    pd.DataFrame: A dataframe summarizing the count and percentage distribution 
                  of the feature, along with the transport status percentages.
    """
    # Calculate the distribution and transport percentages
    summary_df = pd.DataFrame({
        "Count": df[feature].value_counts(),
        "Percentage": df[feature].value_counts(normalize=True) * 100,
        "Transported": df.groupby(feature)[target].value_counts(normalize=True).unstack()[True] * 100,
        "Not Transported": df.groupby(feature)[target].value_counts(normalize=True).unstack()[False] * 100
    })

    # Plot the feature distribution with respect to the target
    sns.countplot(df, x=feature, hue=target)
    plt.title(f'Distribution of {feature} with respect to {target}')
    plt.show()

    # Return the summary dataframe
    return summary_df


def analyze_numerical_feature(df, feature_col, target_col=None, figsize=(15, 6), bins=30):
    """
    Analyze the distribution of a numerical feature and detect outliers.
    Parameters:
    - df: pandas DataFrame, the dataset containing the numerical feature.
    - feature_col: str, the name of the numerical feature column to analyze.
    - target_col: str, the target column to compare against (for the box plot). Optional.
    - figsize: tuple, the size of the figure for the plots.
    - bins: int, the number of bins for the histogram.
    Returns:
    - summary_df: pandas DataFrame, a summary of statistics for the overall feature data and outliers.
    """
    # Check if feature_col exists in the dataframe
    if feature_col not in df.columns:
        raise ValueError(f"Column '{feature_col}' not found in the dataframe.")
    
    # Check if target_col exists in the dataframe (if provided)
    if target_col and target_col not in df.columns:
        raise ValueError(f"Column '{target_col}' not found in the dataframe.")
    
    # Create the figure and subplots
    fig, ax = plt.subplots(2, 1, figsize=figsize, sharex=True)

    # First plot: Histogram with KDE
    sns.histplot(df, x=feature_col, kde=True, ax=ax[0], bins=bins)
    ax[0].set_title(f'Distribution of {feature_col} with KDE')
    ax[0].set_ylabel('Frequency')
    ax[0].grid(True, which='both', linestyle='--', linewidth=0.5)

    # Second plot: Boxplot of the feature by the target (if provided)
    if target_col:
        # Check seaborn version to decide whether to include the 'gap' parameter
        if sns.__version__ >= '0.13':
            sns.boxplot(df, x=feature_col, ax=ax[1], hue=target_col, gap=0.05)
        else:
            sns.boxplot(df, x=feature_col, ax=ax[1], hue=target_col)
        ax[1].set_title(f'Box Plot of {feature_col} by {target_col} Status')
    else:
        sns.boxplot(df, x=feature_col, ax=ax[1])
        ax[1].set_title(f'Box Plot of {feature_col}')

    ax[1].set_ylabel('')
    ax[1].grid(True, which='both', linestyle='--', linewidth=0.5)

    # Adjust layout for better spacing
    plt.tight_layout()

    print(f"Analysis of the {feature_col} column:\n")
    # Display the plots
    plt.show()

    # Calculate overall statistics
    overall_summary = df[feature_col].describe().to_frame().T
    overall_summary.index = [f'{feature_col}_Overall']

    # Calculate the lower and upper bounds for outliers
    Q1 = df[feature_col].quantile(0.25)
    Q3 = df[feature_col].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Identify lower and upper bound outliers
    lower_outliers = df[df[feature_col] < lower_bound]
    upper_outliers = df[df[feature_col] > upper_bound]

    # Get descriptive statistics for lower and upper outliers
    lower_outliers_summary = lower_outliers[feature_col].describe().to_frame().T
    lower_outliers_summary.index = [f'{feature_col}_Lower_Outliers']

    upper_outliers_summary = upper_outliers[feature_col].describe().to_frame().T
    upper_outliers_summary.index = [f'{feature_col}_Upper_Outliers']

    # Combine overall statistics with lower and upper outlier statistics
    summary_df = pd.concat([overall_summary, lower_outliers_summary, upper_outliers_summary])

    # Print the percentage of outliers in the data
    outlier_percentage = ((len(lower_outliers) + len(upper_outliers)) / len(df)) * 100
    lower_outliers_percentage = (len(lower_outliers) / len(df)) * 100
    upper_outliers_percentage = (len(upper_outliers) / len(df)) * 100
    outliers_df = pd.DataFrame({
        'Outlier Percentage': [outlier_percentage],
        'Lower Outliers Percentage': [lower_outliers_percentage],
        'Upper Outliers Percentage': [upper_outliers_percentage]
    })

    return outliers_df, summary_df
