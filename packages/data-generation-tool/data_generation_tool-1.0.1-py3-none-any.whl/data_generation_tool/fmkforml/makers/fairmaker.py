"""
This module contains all necessary tool to
retrieves from a dataset a most fair one.
"""
import pandas as pd
from ortools.sat.python import cp_model

from data_generation_tool.fmkforml.fmk_data.fmkdata import FmkData
from data_generation_tool.fmkforml.utils import init_remove_numerical_col_df, remove_nrecolumns, get_cols_from_df, \
    get_column_recap


def get_most_fair_test_dt(df, coef=.3, remove_num_col=False, remove_nre=-1, columns=[]):
    """
    Compute the most fair test dataset

    # DATASET PREPROCESSING:
    # ----------------------
    # DROP WHICH CONTAIN NULS
    # REMOVE NUMERICAL COLUMN (BY DEFAULT)
    # REMOVE FEATURES WHICH ALL OBSERVATIONS CAN'T BE REPRESENTED (DEFAULT)
    """

    test_dt_size = int(len(df) * coef)
    pre_df = pd.DataFrame(df)
    pre_df.dropna(inplace=True)
    pre_df.drop_duplicates(inplace=True)
    pre_df.reset_index(inplace=True, drop=True)

    if len(pre_df) == 0:
        return

    fair_test_df = pd.DataFrame(pre_df)

    if remove_num_col:
        pre_df = init_remove_numerical_col_df(pre_df)

    if remove_nre > 0:
        pre_df = remove_nrecolumns(pre_df, test_dt_size, remove_nre)

    if len(columns) > 0:
        pre_df = get_cols_from_df(pre_df, set(columns))

    tmp_df = pre_df.copy()

    # VARIABLES AND CONSTRAINTS
    # -------------------------
    # TEST LEN SHOULD BE test_dt_size

    ideal_features_weight = []
    for col in tmp_df:
        _keys = get_column_recap(tmp_df, col)
        val = (test_dt_size // len(_keys.keys()))

        val = 1 if val == 0 else val
        ideal_features_weight.append(val)

    fdata = FmkData(tmp_df.values.tolist())
    model = cp_model.CpModel()
    selected_ind = [model.NewBoolVar("%d" % i) for i in range(len(tmp_df))]
    model.Add(sum(selected_ind) == int(test_dt_size))

    # OPTIMIZATION
    min_funct = __get_min_function(fdata, ideal_features_weight,
                                   model, selected_ind)

    model.Minimize(sum(min_funct))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # SOLUTION
    if status == cp_model.OPTIMAL:
        fair_test_df = __get_solution(solver=solver,
                                      selected_ind=selected_ind,
                                      initial_df=fair_test_df
                                      )
    else:
        return None

    return fair_test_df


def __get_min_function(fdata, ideal_features_weight,
                       model: cp_model.CpModel, selected_ind):
    """
    """
    min_funct = []
    for i in range(len(fdata.data)):
        for key in fdata.data[i]:
            abs_val = model.NewIntVar(0, 99999, '')
            model.AddAbsEquality(abs_val, (((
                sum((ind * fdata.data[i][key][ind.Index()])
                    for ind in selected_ind)
            ))) - ideal_features_weight[i])

            min_funct.append(abs_val)
    return min_funct


def __get_solution(solver: cp_model.CpSolver, selected_ind, initial_df: pd.DataFrame):
    """
    """

    fair_test_df = initial_df.copy()

    for i in range(len(selected_ind)):
        if solver.Value(selected_ind[i]) == 0:
            fair_test_df.drop(axis=0, index=i, inplace=True)
    return fair_test_df
