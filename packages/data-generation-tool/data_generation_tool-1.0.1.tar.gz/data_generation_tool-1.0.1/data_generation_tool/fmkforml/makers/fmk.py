"""
Fmk module
"""
import pandas as pd

from data_generation_tool.fmkforml.checkers.fairchecker import get_fairness
from data_generation_tool.fmkforml.makers.fairmaker import get_most_fair_test_dt


class Fmk:
    """
    Fair Maker object
    """

    def __init__(self, df) -> None:
        """
        Init fmk obj with a dataframe
        """
        self.coef = 0
        self.df = pd.DataFrame(df)
        self.df_test = self.df.sample(int(len(self.df) * 0.3))

    def fairtest(self, coef=.5, rmv_numeric=False, rmv_nre=-1):
        """
        Compute the fairer possible test dataset
        coef(float): define dataset size
        rmv_numeric(boolean): remove or not numeric column
        rmv_nre(int):
        """
        self.df_test = get_most_fair_test_dt(self.df, coef=coef, remove_num_col=rmv_numeric, remove_nre=rmv_nre)

    def test_score(self):
        return get_fairness(self.df_test)
