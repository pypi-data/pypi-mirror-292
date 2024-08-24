"""
This module contain representation of data used
in fmk tool.
"""


class DataColumn:
    """
    Column of a dataframe
    """

    def __init__(self, array=[]):
        """
        init indexes of col
        """
        self.indexes = array


class FmkData:
    """
    Dataset representation
    """

    def __init__(self, df_list: list) -> None:
        """
        """
        self.data = [{} for _ in range(len(df_list[0]))]
        # Create a tab of dict
        for i in range(len(df_list)):
            for j in range(len(df_list[i])):
                if not df_list[i][j] in self.data[j]:
                    self.data[j][(df_list[i][j])] = [0] * len(df_list)
                self.data[j][(df_list[i][j])][i] = 1
