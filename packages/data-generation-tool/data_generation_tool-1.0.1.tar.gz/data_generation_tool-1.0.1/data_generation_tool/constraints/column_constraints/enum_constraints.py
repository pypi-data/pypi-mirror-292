from data_generation_tool.constraints.column_constraints import ColumnConstraint
from data_generation_tool.types import Enum


class EnumConstraint(ColumnConstraint):
    """
    Base class for constraints that can be applied to enum columns
    """

    def target_column_type(self) -> type:
        return Enum


class Allowed(EnumConstraint):
    """
    Indicate that only some values should be accepted for the column

    Attributes
    ----------
        value: list
            The list of values allowed
    """

    def __init__(self, value: list):
        self.value = value


class Forbidden(EnumConstraint):
    """
    Indicate that some values should be never be generated for the column

    Attributes
    ----------
        value: list
            The list of forbidden values
    """

    def __init__(self, value: list):
        self.value = value


class MinSize(EnumConstraint):
    """
    Indicate that the value's size should be longer than the given length

    Attributes
    ----------
        value: int
            The min length of the enum value

    Raises
    -------
        ValueError
            If `value` is lower than 0.
    """

    def __init__(self, value: int):
        if value < 0:
            raise ValueError("value must be non negative")

        self.value = value


class MaxSize(EnumConstraint):
    """
    Indicate that the value's size should be shorter than the given length

    Attributes
    ----------
        value: int
            The max length of the enum value

    Raises
    -------
        ValueError
            If `value` is lower than 0.
    """

    def __init__(self, value: int):
        if value < 0:
            raise ValueError("value must be non negative")

        self.value = value


class SizeInterval(EnumConstraint):
    """
    Indicate that the value's size should be in the given interval

    Attributes
    ----------
        lower_bound: int
            The minimum length of the enum value
        upper_bound: int
            The maximum length of the enum value

    Raises
    -------
        ValueError
            If `lower_bound` < 0 or `upper_bound` < 0 or `lower_bound` > `upper_bound`.
    """

    def __init__(self, lower_bound: int, upper_bound: int):
        if lower_bound < 0 or upper_bound < 0:
            raise ValueError("lower_bound and upper_bound must be non negative")

        if lower_bound > upper_bound:
            raise ValueError("lower_bound must be less than or equal to upper_bound")

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class By(EnumConstraint):
    """
    Indicate that the value should be filtered by a certain criterion

    Attributes
    ----------
        criterion: str
            The criterion by which to filter the values (e.g., continent, type)
        value: str
            The value of the criterion (e.g., 'Europe', 'News')
    """

    def __init__(self, criterion: str, value: str):
        self.criterion = criterion
        self.value = value
