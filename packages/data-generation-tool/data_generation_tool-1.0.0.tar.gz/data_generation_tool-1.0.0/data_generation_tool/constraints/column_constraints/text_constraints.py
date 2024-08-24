from data_generation_tool.constraints.column_constraints.column_constraint import ColumnConstraint
from data_generation_tool.types import Text, E164PhoneNumber
from data_generation_tool.utils import COUNTRIES_PHONE_CODES


class TextConstraint(ColumnConstraint):
    """
        Base class for constraints that are related to text values
    """

    def target_column_type(self) -> type:
        return Text


class Regex(TextConstraint):
    """
    Indicate that the generated text should follow the given regular expression

    Attributes
    ----------
        value: str
            The regular expression to match
    """

    def __init__(self, value: str):
        self.value = value


class MinLength(TextConstraint):
    """
    Indicate that the text should be longer than the given length

    Attributes
    ----------
        value: int
            The min length of the text

    Raises
    -------
        ValueError
            If `value` is lower than 0.
    """

    def __init__(self, value: int):
        if value < 0:
            raise ValueError("value must be non negative")

        self.value = value


class MaxLength(TextConstraint):
    """
    Indicate that the text should be shorter than the given length

    Attributes
    ----------
        value: int
            The max length of the text

    Raises
    -------
        ValueError
            If `value` is lower than 0.
    """

    def __init__(self, value: int):
        if value < 0:
            raise ValueError("value must be non negative")

        self.value = value


class LengthInterval(TextConstraint):
    """
    Indicate that the text length should be in an interval

    Attributes
    ----------
        lower_bound: int
            The minimum length of the text
        upper_bound: int
            The maximum length of the text

    Raises
    -------
        ValueError
            If `lower_bound` < 0 or `upper_bound` < 0 or `lower_bound` > `upper_bound`.
    """

    def __init__(self, lower_bound: int, upper_bound: int):
        if lower_bound < 0 or upper_bound < 0:
            raise ValueError("lower_bound and upper_bound must be non negative")

        if lower_bound > upper_bound:
            raise ValueError("lower_bound must be less than or equal to upper_bound")

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class AllowedWords(TextConstraint):
    """
    Indicate that the text should only contain some given words

    Attributes
    ----------
        value: list[str]
            The allowed words

    Raises
    -------
        ValueError
            if `value` is empty.
    """

    def __init__(self, value: list[str]):
        if not value:
            raise ValueError("value cannot be empty")

        self.value = value


class ForbiddenWords(TextConstraint):
    """
    Indicate that the text should never contain some given words

    Attributes
    ----------
        value: list[str]
            The forbidden words
    """

    def __init__(self, value: list[str]):
        self.value = value


class MinWords(TextConstraint):
    """
    Indicate that the text contains at least a given number of words

    Attributes
    ----------
        value: int
            The min number of words of the text

    Raises
    -------
        ValueError
            If `value` is lower than 0.
    """

    def __init__(self, value: int):
        if value < 0:
            raise ValueError("value must be non negative")

        self.value = value


class MaxWords(TextConstraint):
    """
    Indicate that the text contains at most a given number of words

    Attributes
    ----------
        value: int
            The max number of words of the text

    Raises
    -------
        ValueError
            If `value` is lower than 0.
    """

    def __init__(self, value: int):
        if value < 0:
            raise ValueError("value must be non negative")

        self.value = value


class WordsInterval(TextConstraint):
    """
    Indicate that the text contains at most a given number of words

    Attributes
    ----------
        lower_bound: int
            The minimum number of words of the text
        upper_bound: int
            The maximum number of words of the text

    Raises
    -------
        ValueError
            If `lower_bound` < 0 or `upper_bound` < 0 or `lower_bound` > `upper_bound`.
    """

    def __init__(self, lower_bound: int, upper_bound: int):
        if lower_bound < 0 or upper_bound < 0:
            raise ValueError("lower_bound and upper_bound must be non negative")

        if lower_bound > upper_bound:
            raise ValueError("lower_bound must be less than or equal to upper_bound")

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class PhoneConstraint(TextConstraint):
    """
    Base class for constraints that are related to phone numbers
    """

    def target_column_type(self) -> type:
        return E164PhoneNumber


class CountryPhoneCode(TextConstraint):
    """
    Indicate that the phone numbers generated should have a prefix indicated by the phone code of a specific country

    Attributes
    ----------
        code: str
            The ISO code of the country

    Raises
    -------
        ValueError
            If the `code` is not recognized.
    """

    def __init__(self, code: str):
        if code not in COUNTRIES_PHONE_CODES:
            raise ValueError("code not found for a country")

        self.code = code
