import string

from data_generation_tool.constraints.column_constraints import MinLength, MaxLength, LengthInterval
from data_generation_tool.errors import UnsatisfiableConstraints
from data_generation_tool.generators import ColumnGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import URL


class URLGenerator(ColumnGenerator):
    """
    Generator used for URL generation
    The urls have the form

    https://domain/resource
    where domain have the form <part>.<tld>

    Notes :
        The constraints Regex, AllowedWords, ForbiddenWords, MinWords, MaxWords and WordsInterval are ignored
    """

    def generate(self, column: ColumnGenerationRequest, count: int) -> list:
        if column.column_type != URL:
            raise ValueError(f"Column type {column.column_type} is not E164PhoneNumber")

        # Only the length constraints are applied
        min_len = None
        max_len = None
        for constraint in column.constraints:
            if isinstance(constraint, MinLength):
                min_len = constraint.value

            elif isinstance(constraint, MaxLength):
                max_len = constraint.value

            elif isinstance(constraint, LengthInterval):
                min_len = constraint.lower_bound
                max_len = constraint.upper_bound

        if min_len is not None and max_len is not None and min_len > max_len:
            raise UnsatisfiableConstraints("The minimum length should be less than the maximum length")

        if min_len is not None and min_len < 13:
            raise UnsatisfiableConstraints("The minimum length should be at least 13")

        if min_len is None:
            if max_len is None:
                min_len = 15
            else:
                min_len = max(13, max_len - 5)

        if max_len is None:
            max_len = min_len + 15

        values = []
        for _ in range(count):
            candidate_string = 'https://'
            length_researched = self.rng.integers(min_len, max_len, endpoint=True) - 8
            tld = self.rng.choice([x for x in _tlds if len(x) <= length_researched - 4])
            length_researched -= len(tld)
            part_len = self.rng.integers(2, length_researched - 1, endpoint=True)
            length_researched -= part_len + 1
            part = self._generate_random_string(part_len)
            candidate_string = candidate_string + part + '.' + tld

            if length_researched == 1:
                candidate_string = candidate_string + '/'
            elif length_researched > 1:
                candidate_string = candidate_string + '/' + self._generate_random_string(length_researched - 1)

            values.append(candidate_string)
        return self.post_processing(values, column.constraints)

    def _generate_random_string(self, n: int) -> str:
        chars = list(string.ascii_letters + string.digits)
        return ''.join(self.rng.choice(chars) for _ in range(n))


# Some random that will be used to generate random emails
_tlds = [
    '.com',
    '.net',
    '.org',
    '.edu',
    '.gov',
    '.int',
    '.mil',
    '.co',
    '.biz',
    '.info',
    '.name',
    '.museum',
    '.coop',
    '.aero',
    '.xxx',
    '.xyz',
    '.io',
    '.tk'
]
