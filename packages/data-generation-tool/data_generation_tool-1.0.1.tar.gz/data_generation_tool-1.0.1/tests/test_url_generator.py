import pytest

from data_generation_tool.constraints.column_constraints import Interval, MinLength, MaxLength, LengthInterval
from data_generation_tool.generators import URLGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Numeric, URL


class TestURLGenerator:
    def test_url_generator_generation_with_unsupported_column_type(self):
        with pytest.raises(ValueError) as _:
            _ = URLGenerator().generate(
                column=ColumnGenerationRequest(
                    column_type=Numeric,
                    name="Dummy",
                    constraints=[
                        Interval(100, 10)
                    ]
                ),
                count=4
            )

    def test_url_generation_without_constraints(self):
        data = URLGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=URL,
                name="Bar",
                constraints=[]
            ), count=4)

        assert len(data) == 4
        assert all(x.startswith('https://') for x in data)
        assert all('.' in x for x in data)

    def test_url_generation_with_min_length_constraint(self):
        data = URLGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=URL,
                name="Bar",
                constraints=[MinLength(15)]
            ), count=4)

        assert len(data) == 4
        assert all(x.startswith('https://') for x in data)
        assert all('.' in x for x in data)
        assert all(len(x) >= 15 for x in data)

    def test_url_generation_with_max_length_constraint(self):
        data = URLGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=URL,
                name="Bar",
                constraints=[MaxLength(25)]
            ), count=4)

        assert len(data) == 4
        assert all(x.startswith('https://') for x in data)
        assert all('.' in x for x in data)
        assert all(len(x) <= 25 for x in data)

    def test_url_generation_with_length_interval_constraint(self):
        data = URLGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=URL,
                name="Bar",
                constraints=[LengthInterval(lower_bound=15, upper_bound=25)]
            ), count=4)

        assert len(data) == 4
        assert all(x.startswith('https://') for x in data)
        assert all('.' in x for x in data)
        assert all(15 <= len(x) <= 25 for x in data)
