from pandas.api.types import is_numeric_dtype

def check_type(df, col):
    """Checks if the selected column is numeric."""
    if is_numeric_dtype(df[col]):
        return True
    return False

def get_summary_column(df,col):
    """Generates statistical summary for the selected numerical column."""
    if not check_type(df,col):
        return f"Hata: '{col}' sütunu sayısal değil, analiz yapılamaz."

    return df[col].agg(["mean","std","max","min","sum"]).round(2)

def get_summary_table(df,col1,col2):
    """Groups by one column and displays statistics of another numerical column."""
    if not check_type(df,col2):
        return f"Hata: '{col2}' sütunu sayısal değil, analiz yapılamaz."

    return df.groupby(col1)[col2].agg(["count","mean","std","min","max"]).round(2)

def column_mode(df,col):
    """Returns the most frequently occurring value (mode) of the selected column"""
    return df[col].mode()

def count_NaN(df, col1):
    """Returns the number of missing (NaN) values in the selected column."""
    return df[col1].isna().sum()

def filterby_value(df,col1,value):
    """Filters rows where the selected column equals the entered value."""
    return df[df[col1] == value]

def groupby_mode(df,col1,col2):
    """Groups by one column and shows the mode of the other column for each group."""
    return df.groupby(col1)[col2].apply(lambda x:x.mode() if not x.mode().empty else None)