import pytest

from data_generation_tool.constraints.column_constraints import Minimum, Maximum, Interval, Precision, Positive, \
    Negative, Different
from data_generation_tool.generators import FloatGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Float, Text


class TestFloatGenerator:
    def test_float_generator_generation_with_unsupported_column_type(self):
        with pytest.raises(ValueError) as _:
            _ = FloatGenerator().generate(
                column=ColumnGenerationRequest(
                    column_type=Text,
                    name="Dummy",
                    constraints=[
                        Interval(100, 10)
                    ]
                ),
                count=4
            )

    def test_float_generation_without_constraints(self):
        data = FloatGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Float,
                name="Bar",
                constraints=[]
            ), count=4)

        assert len(data) == 4

    def test_float_generation_with_minimum_constraint(self):
        data = FloatGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Float,
                name="Bar",
                constraints=[
                    Minimum(10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x >= 10 for x in data)

    def test_float_generation_with_maximum_constraint(self):
        data = FloatGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Float,
                name="Bar",
                constraints=[
                    Maximum(10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x <= 10 for x in data)

    def test_float_generation_with_interval_constraint(self):
        data = FloatGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Float,
                name="Bar",
                constraints=[
                    Interval(lower_bound=8, upper_bound=10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(8 <= x <= 10 for x in data)

    def test_number_generation_with_positive_constraint(self):
        data = FloatGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Float,
                name="Bar",
                constraints=[
                    Positive()
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x >= 0 for x in data)

    def test_number_generation_with_negative_constraint(self):
        data = FloatGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Float,
                name="Bar",
                constraints=[
                    Negative()
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x <= 0 for x in data)

    def test_number_generation_with_different_constraint(self):
        data = FloatGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Float,
                name="Bar",
                constraints=[
                    Different(0)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x != 0 for x in data)

    def test_float_generation_with_decimal_part(self):
        data = FloatGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Float,
                name="Bar",
                constraints=[
                    Precision(3),
                    Interval(lower_bound=6, upper_bound=10)
                ]
            ), count=4)

        assert len(data) == 4
        # Count the x. in the string representation and there may be trailing 0's
        assert all(len(str(x).split('.')[1]) <= 3 for x in data)
