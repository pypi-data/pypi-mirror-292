import pytest

from data_generation_tool.constraints.column_constraints import Minimum, Maximum, Interval, Positive, \
    Negative, Different, Uniform, Normal, Exponential
from data_generation_tool.generators import NumberGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Numeric, Text


class TestNumberGenerator:
    def test_number_generator_generation_with_unsupported_column_type(self):
        with pytest.raises(ValueError) as _:
            _ = NumberGenerator().generate(
                column=ColumnGenerationRequest(
                    column_type=Text,
                    name="Dummy",
                    constraints=[
                        Interval(100, 10)
                    ]
                ),
                count=4
            )

    def test_number_generation_without_constraints(self):
        data = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Bar",
                constraints=[]
            ), count=4)

        assert len(data) == 4

    def test_number_generation_with_minimum_constraint(self):
        data = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Bar",
                constraints=[
                    Minimum(10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x >= 10 for x in data)

    def test_number_generation_with_maximum_constraint(self):
        data = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Bar",
                constraints=[
                    Maximum(10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x <= 10 for x in data)

    def test_number_generation_with_interval_constraint(self):
        data = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Bar",
                constraints=[
                    Interval(lower_bound=8, upper_bound=10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(8 <= x <= 10 for x in data)

    def test_number_generation_with_positive_constraint(self):
        data = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Bar",
                constraints=[
                    Positive()
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x >= 0 for x in data)

    def test_number_generation_with_negative_constraint(self):
        data = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Bar",
                constraints=[
                    Negative()
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x <= 0 for x in data)

    def test_number_generation_with_different_constraint(self):
        data = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Bar",
                constraints=[
                    Different(0)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x != 0 for x in data)

    def test_number_generation_with_uniform_distribution(self):
        data = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Bar",
                constraints=[
                    Uniform(lower_bound=5, upper_bound=10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(5 <= x <= 10 for x in data)

    def test_number_generation_with_normal_distribution(self):
        data = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Bar",
                constraints=[Normal(mean=5, standard_deviation=1)]
            ), count=4)

        assert len(data) == 4
        assert all(3 <= x <= 7 for x in data)

    def test_number_generation_with_exponential_distribution(self):
        data = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Bar",
                constraints=[Exponential(scale=5), Interval(lower_bound=3, upper_bound=7)]
            ), count=4)

        assert len(data) == 4
        assert all(3 <= x <= 7 for x in data)
