from data_generation_tool.constraints.column_constraints import ColumnConstraint


class DatasetConstraint:
    """
    Base class for dataset global constraints.

    Attributes
    ----------
        columns_and_constraints: dict[str, ColumnConstraint]
            The list of columns with the constraint to check,the column's data against
    """

    def __init__(self, columns_and_constraints: dict[str, ColumnConstraint]):
        self.columns_and_constraints = columns_and_constraints


class NoneOf(DatasetConstraint):
    """
    None of the given constraints should be satisfied.

    Attributes
    ----------
        columns_and_constraints: dict[str, ColumnConstraint]
            The list of columns with the constraint to check,the column's data against
    """

    def __init__(self, columns_and_constraints: dict[str, ColumnConstraint]):
        super().__init__(columns_and_constraints)
        self.columns_and_constraints = columns_and_constraints


class AtLeast(DatasetConstraint):
    """
    At least `count` lines should satisfy the given constraints for the given columns.

    Attributes
    ----------
        columns_and_constraints: dict[str, ColumnConstraint]
            The list of columns with the constraint to check,the column's data against

    Raises
    -------
        ValueError
            If `count` is lower than 0.
    """

    def __init__(self, columns_and_constraints: dict[str, ColumnConstraint], count: int):
        if count < 0:
            raise ValueError("count should be non-negative")

        super().__init__(columns_and_constraints)
        self.count = count


class AtMost(DatasetConstraint):
    """
    At most `count` lines should satisfy the given constraints for the given columns.

    Attributes
    ----------
        columns_and_constraints: dict[str, ColumnConstraint]
            The list of columns with the constraint to check,the column's data against

    Raises
    -------
        ValueError
            If `count` is lower than 0.
    """

    def __init__(self, columns_and_constraints: dict[str, ColumnConstraint], count: int):
        if count < 0:
            raise ValueError("count should be non-negative")

        super().__init__(columns_and_constraints)
        self.count = count
