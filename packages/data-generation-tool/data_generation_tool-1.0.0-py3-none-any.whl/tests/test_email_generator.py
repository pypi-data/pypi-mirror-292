import pytest

from data_generation_tool.constraints.column_constraints import Interval, MinLength, MaxLength, LengthInterval
from data_generation_tool.generators import EmailGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Numeric, Email


class TestEmailGenerator:
    def test_email_generator_generation_with_unsupported_column_type(self):
        with pytest.raises(ValueError) as _:
            _ = EmailGenerator().generate(
                column=ColumnGenerationRequest(
                    column_type=Numeric,
                    name="Dummy",
                    constraints=[
                        Interval(100, 10)
                    ]
                ),
                count=4
            )

    def test_email_generation_without_constraints(self):
        data = EmailGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Email,
                name="Bar",
                constraints=[]
            ), count=4)
        assert len(data) == 4
        assert all('@' in x for x in data)
        assert all('.' in x for x in data)

    def test_email_generation_with_min_length_constraint(self):
        data = EmailGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Email,
                name="Bar",
                constraints=[
                    MinLength(10)
                ]
            ), count=4)
        assert len(data) == 4
        assert all('@' in x for x in data)
        assert all('.' in x for x in data)
        assert all(len(x) >= 10 for x in data)

    def test_email_generation_with_max_length_constraint(self):
        data = EmailGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Email,
                name="Bar",
                constraints=[
                    MaxLength(10)
                ]
            ), count=4)
        assert len(data) == 4
        assert all('@' in x for x in data)
        assert all('.' in x for x in data)
        assert all(len(x) <= 10 for x in data)

    def test_email_generation_with_length_interval_constraint(self):
        data = EmailGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Email,
                name="Bar",
                constraints=[
                    LengthInterval(lower_bound=10, upper_bound=20)
                ]
            ), count=4)
        assert len(data) == 4
        assert all('@' in x for x in data)
        assert all('.' in x for x in data)
        assert all(10 <= len(x) <= 20 for x in data)
