import pytest

from data_generation_tool.constraints.column_constraints import AllowMissing
from data_generation_tool.generators import EmailGenerator, NumberGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Email, Numeric


class TestGenerationWithMissingValues:
    def test_constraint_raises_exception_with_invalid_percentage(self):
        with pytest.raises(ValueError) as _:
            _ = EmailGenerator().generate(
                column=ColumnGenerationRequest(
                    column_type=Email,
                    name="Emails",
                    constraints=[AllowMissing(percentage=150)]
                ), count=10)


    def test_generation_with_half_missing(self):
        emails = EmailGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Email,
                name="Emails",
                constraints=[AllowMissing(percentage=50)]
            ), count=10)

        none_emails = [email for email in emails if email is None]
        assert len(none_emails) == 5

    def test_generation_with_default_threshold(self):
        numbers = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Number",
                constraints=[AllowMissing()]
            ), count=10)

        none_numbers = [email for email in numbers if email is None]
        assert len(none_numbers) == 2

    def test_normal_data_generated_does_not_contain_none(self):
        numbers = NumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Numeric,
                name="Number",
            ), count=10)

        none_numbers = [email for email in numbers if email is None]
        assert len(none_numbers) == 0
