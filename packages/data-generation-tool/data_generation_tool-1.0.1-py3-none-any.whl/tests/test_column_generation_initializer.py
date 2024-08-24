import pytest

from data_generation_tool.constraints.column_constraints import MinLength, AllowMissing
from data_generation_tool.constraints.column_constraints.numeric_constraints import Minimum, Interval, Prime, Different
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Numeric, Email, Float


class TestColumnGenerationInitializer:
    def test_numeric_column_with_text_constraints(self):
        with pytest.raises(ValueError) as _:
            _ = ColumnGenerationRequest(
                column_type=Numeric,
                name="Dummy",
                constraints=[
                    MinLength(5)
                ]
            )

    def test_numeric_column_with_numeric_constraints(self):
        _ = ColumnGenerationRequest(
            column_type=Numeric,
            name="Dummy",
            constraints=[
                Minimum(5),
                Interval(1, 10)
            ]
        )

        assert 1 == 1

    def test_numeric_column_with_invalid_numeric_constraints(self):
        with pytest.raises(ValueError) as _:
            _ = ColumnGenerationRequest(
                column_type=Numeric,
                name="Dummy",
                constraints=[
                    Interval(100, 10)
                ]
            )

    def test_floating_point_column_with_numeric_constraints(self):
        _ = ColumnGenerationRequest(
            column_type=Float,
            name="Dummy",
            constraints=[
                Different(0)
            ]
        )

        assert 1 == 1

    def test_floating_point_column_with_integer_constraints(self):
        with pytest.raises(ValueError) as _:
            _ = ColumnGenerationRequest(
                column_type=Float,
                name="Dummy",
                constraints=[
                    Prime()
                ]
            )

    def test_numeric_column_with_generic_constraints(self):
        _ = ColumnGenerationRequest(
            column_type=Numeric,
            name="Dummy",
            constraints=[
                AllowMissing()
            ]
        )

        assert 1 == 1

    def test_email_column_with_text_constraints(self):
        _ = ColumnGenerationRequest(
            column_type=Email,
            name="Dummy",
            constraints=[
                MinLength(4)
            ]
        )

        assert 1 == 1
