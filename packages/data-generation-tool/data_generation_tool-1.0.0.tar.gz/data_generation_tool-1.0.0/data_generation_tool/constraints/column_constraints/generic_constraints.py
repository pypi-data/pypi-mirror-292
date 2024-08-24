from data_generation_tool.constraints.column_constraints import ColumnConstraint
from data_generation_tool.types import Any


class GenericConstraint(ColumnConstraint):
    """
    Base class for constraints that can be applied to any type of column of the dataset
    """

    def target_column_type(self) -> type:
        return Any


class AllowMissing(GenericConstraint):
    """
    Indicate that a column allows missing values

    Attributes
    ----------
        percentage: int | float
            The percentage of missing values allowed, if this parameter is absent, a threshold of 20% will be applied

    Raises
    -------
        ValueError
            If `percentage` is not between 0 and 100 (exclusive).
    """

    def __init__(self, percentage: int | float | None = None):
        if percentage is not None and (0 >= percentage or 100 <= percentage):
            raise ValueError("percentage must be between 0 and 100 (exclusive)")

        self.percentage = percentage


class Unique(GenericConstraint):
    """
    Indicate that a column should never contain duplicates
    """
    pass
