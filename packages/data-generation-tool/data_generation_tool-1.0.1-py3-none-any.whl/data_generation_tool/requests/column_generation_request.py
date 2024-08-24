from data_generation_tool.constraints.column_constraints import ColumnConstraint


class ColumnGenerationRequest:
    """
    Describe a column of the dataset

    Attributes
    ----------
        name: str
            Name of the column
        constraints: list[ColumnConstraint]
            Constraints of the column
        fair: bool
            Whether the data generated should be fair or not

    Raises
    -------
        ValueError
            If a constraint is not appropriate to the column type it has been assigned to.
    """

    def __init__(self, name: str, column_type: type, constraints: list[ColumnConstraint] = None, fair: bool = False):
        if constraints is None:
            constraints = []

        for constraint in constraints:
            if not issubclass(column_type, constraint.target_column_type()):
                raise ValueError(f"Constraint type ${constraint.target_column_type()} is not appropriate to column "
                                 f"type ${column_type}")
        self.name = name
        self.column_type = column_type
        self.constraints = constraints
        self.fair = fair
