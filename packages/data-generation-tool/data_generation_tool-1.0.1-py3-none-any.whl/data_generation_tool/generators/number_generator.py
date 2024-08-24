import numpy as np

from data_generation_tool.constraints.column_constraints import (Interval, Prime, Different, MultipleOf,
                                                                 ColumnConstraint, Minimum, Maximum, Positive, Negative,
                                                                 Precision, NumericConstraint, Uniform, Normal,
                                                                 Exponential)
from data_generation_tool.errors import UnsatisfiableConstraints
from data_generation_tool.generators import ColumnGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Numeric, Integer, Float
from data_generation_tool.utils import PRIMES


class NumberGenerator(ColumnGenerator):
    """
    Generator that handles numeric values generation.

    Serves as base class for the Integer and Float generators.
    Some subtype-specific constraints (`MultipleOf` / `Prime` / `Precision`) will not be considered here but only in the
    children : `IntegerGenerator` and `FloatGenerator`
    """

    def generate(self, column: ColumnGenerationRequest, count: int) -> list:
        if column.column_type != Numeric:
            raise ValueError(f"Column type {column.column_type} is not Numeric")

        values = []
        minimum, maximum, exclusion, _, _, _, distribution = self._process_constraints(column.constraints)

        if distribution is not None:
            if isinstance(distribution, Uniform):
                return self._generate_uniform(distribution.lower_bound, distribution.upper_bound, exclusion, count)
            elif isinstance(distribution, Normal):
                return self._generate_normal(distribution.mean, distribution.standard_deviation, minimum, maximum,
                                             exclusion, count)
            elif isinstance(distribution, Exponential):
                return self._generate_exponential(distribution.scale, minimum, maximum, exclusion, count)

        for _ in range(count):
            generate_integer = self.rng.choice([True, False])
            if generate_integer:
                choice = self.rng.integers(minimum, maximum, endpoint=True)
            else:
                choice = self.rng.uniform(minimum, maximum)

            while choice == exclusion:
                generate_integer = self.rng.choice([True, False])
                if generate_integer:
                    choice = self.rng.integers(minimum, maximum, endpoint=True)
                else:
                    choice = self.rng.uniform(minimum, maximum)
            values.append(choice)

        return self.post_processing(values, column.constraints)

    def _generate_uniform(self, lower_bound: int | float, upper_bound: int | float, exclude: int | float | None,
                          count: int, is_integer: bool = False) -> list:
        """
        Util method to generate numbers using a uniform distribution while potentially excluding a given number.

        Since the uniform distribution already defines a range of values, the range constraints will be ignored

        Returns
        -------
            list
                A list containing the generated values
        """

        numbers = []
        while len(numbers) < count:
            candidates = self.rng.uniform(lower_bound, upper_bound, size=count - len(numbers))

            if is_integer:
                numbers.extend(int(x) for x in candidates[candidates != exclude])
            else:
                numbers.extend(candidates[candidates != exclude])

        return numbers[:count]

    def _generate_normal(self, mean: int | float, std: int | float, lower_bound: int | float, upper_bound: int | float,
                         exclude: int | float | None, count: int, is_integer: bool = False) -> list:
        """
        Util method to generate numbers using a normal distribution while potentially excluding a given number

        Returns
        -------
            list
                A list containing the generated values
        """

        numbers = []
        while len(numbers) < count:
            candidates = self.rng.normal(mean, std, size=count - len(numbers))
            candidates = np.clip(candidates, lower_bound, upper_bound)
            if is_integer:
                numbers.extend(int(x) for x in candidates[candidates != exclude])
            else:
                numbers.extend(candidates[candidates != exclude])

        return numbers[:count]

    def _generate_exponential(self, scale: float, lower_bound: int | float, upper_bound: int | float,
                              exclude: int | float | None, count: int, is_integer: bool = False) -> list:
        """
        Util method to generate numbers using an exponential distribution while potentially excluding a given number

        Returns
        -------
            list
                A list containing the generated values
        """

        numbers = []
        while len(numbers) < count:
            candidates = self.rng.uniform(lower_bound, upper_bound, size=count * 2)
            pdf = np.exp(-candidates / scale) / scale
            max_pdf = np.exp(-lower_bound / scale) / scale
            accept = self.rng.uniform(size=len(candidates)) < pdf / max_pdf
            candidates = candidates[accept]
            if is_integer:
                numbers.extend(int(x) for x in candidates[candidates != exclude])
            else:
                numbers.extend(candidates[candidates != exclude])

        return numbers[:count]

    @staticmethod
    def _process_constraints(constraints: list[ColumnConstraint]) \
            -> tuple[
                int | float, int | float, int | float | None, int | float, int | None, list | None, NumericConstraint | None]:
        """
        Util method to process and verify the correctness of the given constraints
        Returns
        -------
            tuple
                A tuple containing the data extracted from the constraints to generate the numbers
                The structure of this tuple is (Min, Max, Exclusion, Multiplier, DecimalPartDigits, GivenSource, Distribution)
                The GivenSource will be used for Prime numbers and for future features

        Raises
        -------
            UnsatisfiableConstraints
                If the given set of constraints are not satisfiable.
        """
        min_value = None
        max_value = None
        multiplier = 1
        excluded = None
        primes = False
        decimal_digits = None
        distribution = None

        for constraint in constraints:
            if isinstance(constraint, Minimum):
                if min_value is None:
                    min_value = constraint.value
                else:
                    min_value = max(min_value, constraint.value)
            elif isinstance(constraint, Maximum):
                if max_value is None:
                    max_value = constraint.value
                else:
                    max_value = min(max_value, constraint.value)
            elif isinstance(constraint, Interval):
                if min_value is None:
                    min_value = constraint.lower_bound
                else:
                    min_value = max(min_value, constraint.lower_bound)

                if max_value is None:
                    max_value = constraint.upper_bound
                else:
                    max_value = min(max_value, constraint.upper_bound)
            elif isinstance(constraint, Different):
                excluded = constraint.value
            elif isinstance(constraint, MultipleOf):
                multiplier = constraint.value
            elif isinstance(constraint, Positive):
                if min_value is None:
                    min_value = 0
                else:
                    min_value = max(min_value, 0)
            elif isinstance(constraint, Negative):
                if max_value is None:
                    max_value = 0
                else:
                    max_value = min(max_value, 0)
            elif isinstance(constraint, Prime):
                primes = True
            elif isinstance(constraint, Precision):
                decimal_digits = constraint.value
            elif isinstance(constraint, Uniform):
                min_value = constraint.lower_bound
                max_value = constraint.upper_bound
            elif isinstance(constraint, Normal):
                min_value = constraint.mean - 2 * constraint.standard_deviation
                max_value = constraint.mean + 2 * constraint.standard_deviation
            elif isinstance(constraint, Exponential):
                distribution = constraint

        if min_value is not None and max_value is not None and min_value > max_value:
            raise UnsatisfiableConstraints("The minimum value should be less than the maximum value")

        if primes and max_value is not None and max_value < 1:
            raise UnsatisfiableConstraints("There is no prime number less than 1")

        if primes and multiplier != 1:
            raise UnsatisfiableConstraints("A prime number cannot be a multiple of a number different from 1 and "
                                           "itself")

        if min_value is None:
            min_value = -10000

        if max_value is None:
            max_value = 10000

        return min_value, max_value, excluded, multiplier, decimal_digits, PRIMES if primes else None, distribution


class IntegerGenerator(NumberGenerator):
    """
    Generator that handles integer values generation
    """

    def generate(self, column: ColumnGenerationRequest, count: int) -> list:
        if column.column_type != Integer:
            raise ValueError(f"Column type {column.column_type} is not Integer")

        values = []
        minimum, maximum, exclusion, multiplier, _, source, distribution = self._process_constraints(column.constraints)
        if distribution is not None:
            if isinstance(distribution, Uniform):
                return self._generate_uniform(distribution.lower_bound, distribution.upper_bound, exclusion, count)
            elif isinstance(distribution, Normal):
                return self._generate_normal(distribution.mean, distribution.standard_deviation, minimum, maximum,
                                             exclusion, count)
            elif isinstance(distribution, Exponential):
                return self._generate_exponential(distribution.scale, minimum, maximum, exclusion, count)
        if multiplier != 1:
            minimum = int(minimum / multiplier)
            maximum = int(maximum / multiplier)

        source = [item for item in source if minimum <= item <= maximum] if source is not None else None

        for _ in range(count):
            if source is not None:
                choice = self.rng.choice(source)
            else:
                choice = self.rng.integers(minimum, maximum, endpoint=True)

            while choice == exclusion:
                if source is not None:
                    choice = self.rng.choice(source)
                else:
                    choice = self.rng.integers(minimum, maximum, endpoint=True)

            values.append(choice * multiplier)

        return self.post_processing(values, column.constraints)


class FloatGenerator(NumberGenerator):
    """
    Generator that handles integer values generation
    """

    def generate(self, column: ColumnGenerationRequest, count: int) -> list:
        if column.column_type != Float:
            raise ValueError(f"Column type {column.column_type} is not Float")

        values = []
        minimum, maximum, exclusion, multiplier, decimal_digits, _, distribution = self._process_constraints(
            column.constraints)
        if distribution is not None:
            if isinstance(distribution, Uniform):
                return self._generate_uniform(distribution.lower_bound, distribution.upper_bound, exclusion, count)
            elif isinstance(distribution, Normal):
                return self._generate_normal(distribution.mean, distribution.standard_deviation, minimum, maximum,
                                             exclusion, count)
            elif isinstance(distribution, Exponential):
                return self._generate_exponential(distribution.scale, minimum, maximum, exclusion, count)

        for _ in range(count):
            choice = self.rng.uniform(minimum, maximum)
            if decimal_digits is not None:
                choice = round(choice, decimal_digits)

            while choice == exclusion:
                choice = self.rng.uniform(minimum, maximum)
                if decimal_digits is not None:
                    choice = round(choice, decimal_digits)

            values.append(choice * multiplier)

        return self.post_processing(values, column.constraints)
