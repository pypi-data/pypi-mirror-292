import pytest

from data_generation_tool.constraints.column_constraints import Minimum, Maximum, Interval, MultipleOf, Prime, \
    Different, Negative, Positive
from data_generation_tool.generators import IntegerGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Integer, Text


class TestIntegerGenerator:
    def test_integer_generator_generation_with_unsupported_column_type(self):
        with pytest.raises(ValueError) as _:
            _ = IntegerGenerator().generate(
                column=ColumnGenerationRequest(
                    column_type=Text,
                    name="Dummy",
                    constraints=[
                        Interval(100, 10)
                    ]
                ),
                count=4
            )

    def test_integer_generation_without_constraints(self):
        data = IntegerGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Integer,
                name="Bar",
                constraints=[]
            ), count=4)

        assert len(data) == 4

    def test_integer_generation_with_minimum_constraint(self):
        data = IntegerGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Integer,
                name="Bar",
                constraints=[
                    Minimum(10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x >= 10 for x in data)

    def test_integer_generation_with_maximum_constraint(self):
        data = IntegerGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Integer,
                name="Bar",
                constraints=[
                    Maximum(10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x <= 10 for x in data)

    def test_integer_generation_with_interval_constraint(self):
        data = IntegerGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Integer,
                name="Bar",
                constraints=[
                    Interval(lower_bound=8, upper_bound=10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(8 <= x <= 10 for x in data)

    def test_number_generation_with_positive_constraint(self):
        data = IntegerGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Integer,
                name="Bar",
                constraints=[
                    Positive()
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x >= 0 for x in data)

    def test_number_generation_with_negative_constraint(self):
        data = IntegerGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Integer,
                name="Bar",
                constraints=[
                    Negative()
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x <= 0 for x in data)

    def test_number_generation_with_different_constraint(self):
        data = IntegerGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Integer,
                name="Bar",
                constraints=[
                    Different(0)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x != 0 for x in data)

    def test_integer_generation_with_multiple_of_constraint(self):
        data = IntegerGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Integer,
                name="Bar",
                constraints=[
                    MultipleOf(4)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x % 4 == 0 for x in data)

    def test_integer_generation_with_prime_constraint(self):
        data = IntegerGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Integer,
                name="Bar",
                constraints=[
                    Prime(),
                    Interval(lower_bound=6, upper_bound=10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x == 7 for x in data)
