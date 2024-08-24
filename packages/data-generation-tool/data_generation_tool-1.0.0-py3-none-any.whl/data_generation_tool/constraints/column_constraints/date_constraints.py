from datetime import datetime

from data_generation_tool.constraints.column_constraints import ColumnConstraint
from data_generation_tool.types import Date


class DateConstraint(ColumnConstraint):
    """
    Base class for constraints that are related to numeric values
    """

    def target_column_type(self) -> type:
        return Date


class Future(DateConstraint):
    """
    Indicate that the dates generated in the column should be in the future
    """


class Past(DateConstraint):
    """
    Indicate that the dates generated in the column should be in the past
    """


class After(DateConstraint):
    """
    Indicate that the dates generated in the column should occur after a given date

    Attributes
    ----------
        value: datetime
            The minimum date allowed in the column
    """

    def __init__(self, value: datetime):
        self.value = value


class Before(DateConstraint):
    """
    Indicate that the dates generated in the column should occur before a given date

    Attributes
    ----------
        value: datetime
            The maximum date allowed in the column
    """

    def __init__(self, value: datetime):
        self.value = value


class Period(DateConstraint):
    """
    Indicate that the dates generated in the column should be between two given dates

    Attributes
    ----------
        lower_bound: datetime
            The minimum date allowed in the column
        upper_bound: datetime
            The maximum date allowed in the column

    Raises
    -------
        ValueError
            If `lower_bound` occurs before `upper_bound`.
    """

    def __init__(self, lower_bound: datetime, upper_bound: datetime):
        if lower_bound > upper_bound:
            raise ValueError("lower_bound must precede upper_bound")

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class Mode(DateConstraint):
    """
    The generation mode for the dates

    Attributes
    ----------
        value: str

    Raises
    -------
        ValueError
            If `value` is neither "incremental" nor "random".
    """

    def __init__(self, value: str):
        if value != "incremental" and value != "random":
            raise ValueError("Value must be either \"incremental\" or \"random\"")

        self.value = value


class DateFormat(DateConstraint):
    """
    The format followed by the generated dates
    """

    def __init__(self, value: str):
        self.value = value


class IncrementStep(DateConstraint):
    def __init__(self, value: int):
        self.value = value


class IncrementUnit(DateConstraint):
    def __init__(self, value: str):
        self.value = value
