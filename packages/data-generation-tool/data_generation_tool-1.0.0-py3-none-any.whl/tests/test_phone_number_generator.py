import pytest

from data_generation_tool.constraints.column_constraints import Interval, MinLength, MaxLength, LengthInterval, \
    CountryPhoneCode
from data_generation_tool.errors import UnsatisfiableConstraints
from data_generation_tool.generators import E164PhoneNumberGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Numeric, E164PhoneNumber


class TestPhoneNumberGenerator:
    def test_phone_number_generator_generation_with_unsupported_column_type(self):
        with pytest.raises(ValueError) as _:
            _ = E164PhoneNumberGenerator().generate(
                column=ColumnGenerationRequest(
                    column_type=Numeric,
                    name="Dummy",
                    constraints=[
                        Interval(100, 10)
                    ]
                ),
                count=4
            )

    def test_phone_number_generation_without_constraints(self):
        data = E164PhoneNumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=E164PhoneNumber,
                name="Bar",
                constraints=[]
            ), count=4)

        assert len(data) == 4
        assert all(x.startswith('+') for x in data)

    def test_phone_number_generation_with_min_length_constraint(self):
        data = E164PhoneNumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=E164PhoneNumber,
                name="Bar",
                constraints=[
                    MinLength(10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(x.startswith('+') for x in data)
        assert all(len(x) >= 10 for x in data)

    def test_phone_number_generation_with_max_length_constraint(self):
        data = E164PhoneNumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=E164PhoneNumber,
                name="Bar",
                constraints=[
                    MaxLength(10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(len(x) <= 10 for x in data)

    def test_phone_number_generation_with_length_interval_constraint(self):
        data = E164PhoneNumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=E164PhoneNumber,
                name="Bar",
                constraints=[
                    LengthInterval(lower_bound=8, upper_bound=10)
                ]
            ), count=4)

        assert len(data) == 4
        assert all(8 <= len(x) <= 10 for x in data)

    def test_phone_number_generation_with_country_code(self):
        data = E164PhoneNumberGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=E164PhoneNumber,
                name="Bar",
                constraints=[CountryPhoneCode("BJ")]
            ), count=4)

        assert len(data) == 4
        assert all(x.startswith("+229") for x in data)

    def test_phone_number_generator_generation_with_country_code_and_invalid_len(self):
        with pytest.raises(UnsatisfiableConstraints) as _:
            _ = E164PhoneNumberGenerator().generate(
                column=ColumnGenerationRequest(
                    column_type=E164PhoneNumber,
                    name="Bar",
                    constraints=[CountryPhoneCode("BJ"), MaxLength(4)]
                ), count=4)
