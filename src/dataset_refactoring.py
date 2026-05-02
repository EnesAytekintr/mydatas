def delete_by_column(df,col):
    """Deletes all rows containing NaN in the specified column."""
    df.dropna(axis=0, subset=[col], inplace=True)
    return df

def row_deleteby_value(df,i):
    """Deletes rows that have fewer non-null cells than the entered threshold."""
    df.dropna(axis=0, thresh=i, inplace=True)
    return df

def column_deleteby_value(df,i):
    """Deletes columns that have fewer non-null cells than the entered threshold."""
    df.dropna(axis=1,thresh=i,inplace=True)
    return df

def fill_na(df,col,i):
    """Fills NaN values in the selected column with a specified constant value."""
    df[col].fillna(i,inplace=True)
    return df

def delete_by_value(df,col,value):
    """Completely deletes rows that are equal to the specified value in the selected column."""
    df.drop(df[df[col] == value].index, inplace=True)
    return df

def delete_column(df,col):
    """Completely removes the selected column from the dataset."""
    df.drop(columns=[col], errors='ignore', inplace=True)
    return df

def rename_column(df,col,new_col):
    """Renames the selected column with a new name."""
    df.rename(columns={col:new_col},inplace=True)
    return df

def drop_duplicate_column(df,col):
    """Drops duplicate rows based on the selected column, keeping the first instance."""
    df.drop_duplicates(subset=[col],keep="first",inplace=True)
    return df