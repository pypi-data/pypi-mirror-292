from data_generation_tool.constraints.dataset_constraints import DatasetConstraint
from data_generation_tool.requests.column_generation_request import ColumnGenerationRequest


class GenerationRequest:
    """
        Describe the request used to start the dataset generation process

        Attributes
        ----------
           columns: list[ColumnGenerationRequest]
               The list of columns of the dataset
           constraints: list[DatasetConstraint]
               Global constraints of the dataset
           count: int
                Number of lines to generate

        Raises
        -------
            ValueError
                - If count <= 0
                - If no columns are specified
                - If there are columns with duplicated names
                - If there is a dataset constraint on a non-existing column
       """

    def __init__(self, columns: list[ColumnGenerationRequest], count: int, constraints: list[DatasetConstraint] = None):
        if count <= 0:
            raise ValueError('The count cannot be lower or equal to 0')

        if not columns:
            raise ValueError('No columns specified')

        if constraints is None:
            constraints = []

        if len(set(col.name for col in columns)) != len(columns):
            raise ValueError('Columns must have unique names')

        for dataset_constraint in constraints:
            for column_name in dataset_constraint.columns_and_constraints:
                candidates_columns = list(filter(lambda x: x.name == column_name, columns))

                if len(candidates_columns) == 0:
                    raise ValueError(f"Dataset constraint created for the missing column {column_name}")

                matching_column = candidates_columns[0]

                if not issubclass(matching_column.column_type,
                                  dataset_constraint.columns_and_constraints[column_name].target_column_type()):
                    raise ValueError(
                        f"Constraint type "
                        f"${dataset_constraint.columns_and_constraints[column_name].target_column_type()} is not"
                        f"appropriate to column type ${matching_column.column_type}")

        self.columns = columns
        self.constraints = constraints
        self.count = count
