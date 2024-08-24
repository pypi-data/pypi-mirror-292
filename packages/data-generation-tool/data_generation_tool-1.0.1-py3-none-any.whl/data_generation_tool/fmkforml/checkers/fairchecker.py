"""
This module is used to assess a dataset
"""
import pandas as pd


def get_fairness(df):
    """
    Compute the fairness score according to
    the defined formula,
    return 0 if the dataset is totally fair
    """
    _score = 0
    if isinstance(df, pd.DataFrame):
        for column in df:
            _score = _score + get_col_fairness(column, df)
        return _score / len(df.columns)


def get_int_score(df):
    _score = 0
    if isinstance(df, pd.DataFrame):
        for column in df:
            _score = _score + get_int_col_fair_score(column, df)
        return _score


def get_int_col_fair_score(col, df):
    """
    Compute the fairness for a particular
    column.
    """
    if col is None:
        return
    if col not in df:
        return

    col_len = len(df)
    df = pd.DataFrame(df)
    score = 0
    col_recap = df[col].value_counts()
    col_nb_var = len(col_recap)
    for obs in col_recap.keys():
        score += abs(
            (col_recap[obs]) - (col_len // col_nb_var)
        )
    return score


def get_col_fairness(col, df):
    """
    Compute the fairness for a particular
    column.
    """
    if col is None:
        return
    if col not in df:
        return

    col_len = len(df)
    df = pd.DataFrame(df)
    score = 0
    col_recap = df[col].value_counts()
    col_nb_var = len(col_recap)
    for obs in col_recap.keys():
        score += round(abs(
            (col_recap[obs] / col_len) - (1 / col_nb_var)
        ), 2)

    return score


def get_cols_fairness(df, columns=[]):
    """
    Get fairness througth set of colums
    """
    if len(columns) == 0:
        return
    if df is None:
        return

    cols = set(columns)
    score = 0
    for col in cols:
        if col not in df:
            return
        score += get_col_fairness(col, df)
    return score / len(cols)


def __is_totally_fair_possible():
    raise NotImplemented("not yet....")
