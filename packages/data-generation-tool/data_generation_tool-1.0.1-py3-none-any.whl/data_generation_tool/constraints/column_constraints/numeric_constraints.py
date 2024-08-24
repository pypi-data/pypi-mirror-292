from data_generation_tool.constraints.column_constraints.column_constraint import ColumnConstraint
from data_generation_tool.types import Numeric, Integer, Float


class NumericConstraint(ColumnConstraint):
    """
    Base class for constraints that are related to numeric values
    """

    def target_column_type(self) -> type:
        return Numeric


class Minimum(NumericConstraint):
    """
    Indicate that the values generated in the column should be >= to a given value

    Attributes
    ----------
        value: int | float
            The minimum value allowed in the column
    """

    def __init__(self, value: int | float):
        self.value = value


class Maximum(NumericConstraint):
    """
    Indicate that the values generated in the column should be <= to a given value

    Attributes
    ----------
        value: int | float
            The maximum value allowed in the column
    """

    def __init__(self, value: int | float):
        self.value = value


class Interval(NumericConstraint):
    """
    Indicate that the values generated in the column should be in a given range such as min <= generated <= max

    Attributes
    ----------
        lower_bound: int | float
            The minimum value allowed in the column
        upper_bound: int | float
            The maximum value allowed in the column

    Raises
    -------
        ValueError
            If `lower_bound` is greater than `upper_bound`.
    """

    def __init__(self, lower_bound: int | float, upper_bound: int | float):
        if lower_bound > upper_bound:
            raise ValueError("lower_bound must be less than or equal to upper_bound")

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class Different(NumericConstraint):
    """
    Indicate that all the values generated in the column should be different from a given value

    Attributes
    ----------
        value: int | float
            The value forbidden in the column
    """

    def __init__(self, value: int | float):
        self.value = value


class Positive(NumericConstraint):
    """
    Indicate that the values generated should be >= 0
    """
    pass


class Negative(NumericConstraint):
    """
    Indicate that the values generated in the column should be a <= 0
    """
    pass


class Uniform(NumericConstraint):
    """
    Indicate that the values generated follow a uniform distribution
    Note that the distribution constraints will nullify all the other constraints

    Attributes
    ----------
        lower_bound: int | float
            The minimum value for the range
        upper_bound: int | float
            The maximum value for the range

    Raises
    -------
        ValueError
            If `lower_bound` is greater than `upper_bound`.
    """

    def __init__(self, lower_bound: int | float, upper_bound: int | float):
        if lower_bound > upper_bound:
            raise ValueError("lower_bound must be less than or equal to upper_bound")

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class Normal(NumericConstraint):
    """
    Indicate that the values generated follow a uniform distribution
    Note that the distribution constraints will nullify all the other constraints

    Attributes
    ----------
        mean: int | float
            The mean (\mu)
        standard_deviation: int | float
            The standard deviation for the distribution

    Raises
    -------
        ValueError
            If `standard_deviation` is negative.
    """

    def __init__(self, mean: int | float, standard_deviation: int | float):
        if standard_deviation < 0:
            raise ValueError("The standard_deviation must be non-negative")
        self.mean = mean
        self.standard_deviation = standard_deviation


class Exponential(NumericConstraint):
    """
    Indicate that the values generated follow an exponential distribution
    Note that the distribution constraints will nullify all the other constraints

    Attributes
    ----------
        scale: The scale parameter, \beta. Must be non-negative.

    Raises
    -------
        ValueError
            If `scale` is negative.
    """

    def __init__(self, scale: int | float):
        if scale < 0:
            raise ValueError("The scale must be non-negative")

        self.scale = scale


class IntegerConstraint(NumericConstraint):
    """
    Base class for constraints that are related to numeric values
    """

    def target_column_type(self) -> type:
        return Integer


class Prime(IntegerConstraint):
    """
    Indicate that the values generated in the column should be prime numbers
    """
    pass


class MultipleOf(IntegerConstraint):
    """
    Indicate that the values generated in the column should be a multiple of the given value

    Attributes
    ----------
        value: int | float
            The value which must divide all the values generated in the column
    """

    def __init__(self, value: int | float):
        self.value = value


class FloatConstraint(NumericConstraint):
    """
    Base class for constraints that are related to floating point values
    """

    def target_column_type(self) -> type:
        return Float


class Precision(FloatConstraint):
    """
    Indicate that the values generated in the column should have precision decimal digits

    Attributes
    ----------
        value: int
            The number of digits.

    Raises
    -------
        ValueError
            If `value` is lower than 0.
    """

    def __init__(self, value: int):
        if value < 0:
            raise ValueError("value should be non-negative")

        self.value = value
