import pytest

from data_generation_tool.constraints.column_constraints import Interval, MinLength, MaxLength, LengthInterval
from data_generation_tool.generators.name_generator import NameGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Name, Numeric


class TestNameGenerator:
    def test_name_generator_generation_with_unsupported_column_type(self):
        with pytest.raises(ValueError) as _:
            _ = NameGenerator().generate(
                column=ColumnGenerationRequest(
                    column_type=Numeric,
                    name="Dummy",
                    constraints=[
                        Interval(100, 10)
                    ]
                ),
                count=4
            )

    def test_name_generation_without_constraints(self):
        data = NameGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Name,
                name="Bar",
                constraints=[]
            ), count=4)

        assert len(data) == 4

    def test_name_generation_with_min_length_constraint(self):
        data = NameGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Name,
                name="Bar",
                constraints=[
                    MinLength(10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(len(x) >= 10 for x in data)

    def test_name_generation_with_max_length_constraint(self):
        data = NameGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Name,
                name="Bar",
                constraints=[
                    MaxLength(10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(len(x) <= 10 for x in data)

    def test_name_generation_with_length_interval_constraint(self):
        data = NameGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Name,
                name="Bar",
                constraints=[
                    LengthInterval(lower_bound=10, upper_bound=35)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(10 <= len(x) <= 35 for x in data)
