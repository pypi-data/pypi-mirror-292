from abc import abstractmethod, ABC


class ColumnConstraint(ABC):
    """
    Base class for column constraints.
    """

    @abstractmethod
    def target_column_type(self) -> type:
        """
        Returns the target column type.
        Returns
        -------
        type
            The type of column this constraint is applicable to.
        """
        pass


class ExternalColumnConstraint(ColumnConstraint):
    """
    Base class for user-defined constraints : The validation will be done directly in the constraint
    """

    @abstractmethod
    def filter(self, data: list) -> list:
        """
        Filters the data according to the constraints.

        Parameters
        ----------
        data: list

        Returns
        -------
            list
                The filtered data
        """
        pass
