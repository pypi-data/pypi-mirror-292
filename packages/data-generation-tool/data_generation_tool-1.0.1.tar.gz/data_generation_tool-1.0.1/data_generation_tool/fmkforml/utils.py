"""
Utils functions
"""
import pandas as pd


def convert_to_number(s):
    """
    Convert entry to unique number using
    little endian bit order
    """
    return int.from_bytes(s.encode(), 'little')


def remove_numeric_column(df):
    """
    Check and remove numeric columns from the dataset
    """
    _df = pd.DataFrame(df)
    for col in _df:
        if pd.api.types.is_numeric_dtype(_df[col]):
            _df = _df.drop(col, axis=1)
    return _df


def get_cols_from_df(df, columns: set):
    """
    Get columns from df
    """
    if not isinstance(df, pd.DataFrame):
        return

    _df = df.copy()
    for col in _df:
        if col not in columns:
            _df = _df.drop(col, axis=1)

    if len(_df) == 0:
        return df
    return _df


def get_column_recap(df, col):
    return df[col].value_counts()


def init_remove_numerical_col_df(df):
    """
    Set the dataset, to be ready for our cp model :

    - remove null rows

    - remove numerical value column by default
    """
    _df = pd.DataFrame(df)
    _df = remove_numeric_column(_df)
    return _df


def remove_nrecolumns(df: pd.DataFrame, testdf_len: int, min_val=1):
    """
    Used to drop from dataset column
    that can't be represented enough
    """
    _df = df.copy()

    for col in _df:
        _keys = get_column_recap(_df, col)
        val = (testdf_len // len(_keys.keys()))
        if val < min_val:
            _df = _df.drop(col, axis=1)

    return _df
