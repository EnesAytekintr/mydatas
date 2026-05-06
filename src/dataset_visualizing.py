import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype


def check_type(df, col):
    """Checks if the selected column is numeric."""
    if is_numeric_dtype(df[col]):
        return True
    return False


def check_two_type(df, col1, col2):
    """Checks if the selected columns is numeric."""
    if is_numeric_dtype(df[col1]) and is_numeric_dtype(df[col2]):
        return True
    return False


def categorical_sum(df, col1, col2):
    """Groups by a categorical column and displays the sum of a numerical column as a bar chart."""
    if check_type(df, col2):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.set_style("darkgrid")
        ax.set_title(f"Sum of {col2} categoried by {col1}")
        uniques = df[col1].nunique()
        if uniques < 10:
            sns.barplot(x=col1,
                        y=col2,
                        data=df,
                        palette="coolwarm",
                        hue=col1,
                        legend=False,
                        estimator=np.sum,
                        errorbar=None,
                        ax=ax)
            fig.tight_layout()
            return fig
        elif uniques < 30:
            sns.barplot(x=col2,
                        y=col1,
                        data=df,
                        palette="coolwarm",
                        orient="h",
                        hue=col1,
                        legend=False,
                        estimator=np.sum,
                        errorbar=None,
                        ax=ax)
            fig.tight_layout()
            return fig
        else:
            plt.close(fig)
            return "Too many unique values"
    else:
        return f"Hata: '{col2}' sütunu sayısal değil, analiz yapılamaz."


def categorical_mean(df, col1, col2):
    """Groups by a categorical column and displays the mean of a numerical column as a bar chart."""
    if check_type(df, col2):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.set_style("darkgrid")
        ax.set_title(f"Mean of {col2} categoried by {col1}")
        uniques = df[col1].nunique()
        if uniques < 10:
            sns.barplot(x=col1,
                        y=col2,
                        data=df,
                        palette="coolwarm",
                        hue=col1,
                        legend=False,
                        estimator=np.mean,
                        errorbar=None,
                        ax=ax)
            fig.tight_layout()
            return fig
        elif uniques < 30:
            sns.barplot(x=col2,
                        y=col1,
                        data=df,
                        palette="coolwarm",
                        orient="h",
                        hue=col1,
                        legend=False,
                        estimator=np.mean,
                        errorbar=None,
                        ax=ax)
            fig.tight_layout()
            return fig
        else:
            plt.close(fig)
            return "Too many unique values"
    else:
        return f"Hata: '{col2}' sütunu sayısal değil, analiz yapılamaz."


def categorical_std(df, col1, col2):
    """Groups by a categorical column and displays the standard deviation of a numerical column as a bar chart."""
    if check_type(df, col2):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.set_style("darkgrid")
        ax.set_title(f"Standard Deviation of {col2} categoried by {col1}")
        uniques = df[col1].nunique()
        if uniques < 10:
            sns.barplot(x=col1,
                        y=col2,
                        data=df,
                        palette="coolwarm",
                        hue=col1,
                        legend=False,
                        estimator=np.std,
                        errorbar=None,
                        ax=ax)
            fig.tight_layout()
            return fig
        elif uniques < 30:
            sns.barplot(x=col2,
                        y=col1,
                        data=df,
                        palette="coolwarm",
                        orient="h",
                        hue=col1,
                        legend=False,
                        estimator=np.std,
                        errorbar=None,
                        ax=ax)
            fig.tight_layout()
            return fig
        else:
            plt.close(fig)
            return "Too many unique values"
    else:
        return f"Hata: '{col2}' sütunu sayısal değil, analiz yapılamaz."


def distribution(df, col):
    """Displays the distribution of a numerical column as a histogram."""
    if check_type(df, col):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.set_style("darkgrid")
        ax.set_title(f"Distribution of {col}")
        sns.histplot(df[col],
                     kde=False,
                     bins=35,
                     color="#00509d",
                     edgecolor="black",
                     alpha=0.8,
                     linewidth=1,
                     ax=ax)
        fig.tight_layout()
        return fig
    else:
        return f"Hata: '{col}' sütunu sayısal değil, analiz yapılamaz."


def scatter_plot(df, col1, col2, hue=None):
    """Displays the relationship between two numerical columns with a scatter plot."""
    if check_two_type(df, col1, col2):
        if hue is not None:
            hue_len = df[hue].nunique()
            if hue_len > 8:
                return f"Hata: '{hue}' sütununda çok fazla kategori var ({hue_len}). Görselleştirme karmaşıklaşır."
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.set_style("darkgrid")
        ax.set_title(f"{col1} vs {col2}")
        sns.scatterplot(x=col1,
                        y=col2,
                        data=df,
                        hue=hue,
                        palette="viridis",
                        ax=ax)
        if hue:
            ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
        fig.tight_layout()
        return fig
    else:
        return f"Hata: '{col1}, {col2}' sütunları sayısal değil, analiz yapılamaz."


def pie(df, col):
    """Displays the value distribution of a categorical column as a pie chart."""
    pie_data = df[col].value_counts()
    if len(pie_data) > 15:
        return "Too many unique values. Pie Chart is not optimal."
    colors = sns.color_palette("pastel")[0:len(pie_data)]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(f"Piechart of {col}")
    ax.pie(pie_data,
           labels=pie_data.index,
           autopct='%1.1f%%',
           colors=colors)
    fig.tight_layout()
    return fig