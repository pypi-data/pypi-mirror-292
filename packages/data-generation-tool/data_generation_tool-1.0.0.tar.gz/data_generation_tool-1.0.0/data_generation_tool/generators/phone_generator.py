from data_generation_tool.constraints.column_constraints import MinLength, MaxLength, LengthInterval, \
    CountryPhoneCode
from data_generation_tool.errors import UnsatisfiableConstraints
from data_generation_tool.generators import ColumnGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import E164PhoneNumber
from data_generation_tool.utils import COUNTRIES_PHONE_CODES


class E164PhoneNumberGenerator(ColumnGenerator):
    """
    Generator used for e164 formatted phone number values
    The regex to describe them is : `^\+[1-9]\d{1,14}$`.
    They should start by a nonzero digit and have up to 15 digits

    Sources :
    (https://www.twilio.com/docs/glossary/what-e164)

    (https://www.itu.int/rec/T-REC-E.164/en)

    Notes :
        The constraints Regex, AllowedWords, ForbiddenWords, MinWords, MaxWords and WordsInterval are ignored
        The country code can also be defined by a constraint
    """

    def generate(self, column: ColumnGenerationRequest, count: int) -> list:
        if column.column_type != E164PhoneNumber:
            raise ValueError(f"Column type {column.column_type} is not E164PhoneNumber")

        # Only the length constraints are applied
        min_len = None
        max_len = None
        phone_code = None

        for constraint in column.constraints:
            if isinstance(constraint, MinLength):
                min_len = constraint.value
            elif isinstance(constraint, MaxLength):
                max_len = constraint.value
            elif isinstance(constraint, LengthInterval):
                min_len = constraint.lower_bound
                max_len = constraint.upper_bound
            elif isinstance(constraint, CountryPhoneCode):
                phone_code = COUNTRIES_PHONE_CODES[constraint.code]

        if phone_code is not None and max_len is not None and max_len <= len(phone_code) + 1:
            raise UnsatisfiableConstraints(
                "The maximum length should not be less than the pĥone size given the country code")

        if min_len is not None and max_len is not None and min_len > max_len:
            raise UnsatisfiableConstraints("The minimum length should be less than the maximum length")

        if max_len is not None and max_len > 16:
            raise UnsatisfiableConstraints("The phone number cannot exceed 16 characters")

        if min_len is not None and min_len < 2:
            raise UnsatisfiableConstraints("The minimum length should be at least 2")

        if min_len is None:
            min_len = 8

        if max_len is None:
            max_len = 16

        values = []
        for _ in range(count):
            if phone_code is None:
                length = self.rng.integers(min_len, max_len, endpoint=True) - 2
                start = 10 ** (length - 1)
                end = 10 ** length - 1
                candidate_string = '+' + str(self.rng.integers(1, 9, endpoint=True)) + str(
                    self.rng.integers(start, end, endpoint=True))
                values.append(candidate_string)
            else:
                length = self.rng.integers(min_len, max_len, endpoint=True) - len(phone_code)
                start = 10 ** (length - 1)
                end = 10 ** length - 1
                candidate_string = phone_code + str(self.rng.integers(start, end, endpoint=True))
                values.append(candidate_string)
        return self.post_processing(values, column.constraints)
