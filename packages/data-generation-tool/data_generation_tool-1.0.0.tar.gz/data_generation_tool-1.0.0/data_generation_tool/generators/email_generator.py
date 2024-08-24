import string

from data_generation_tool.constraints.column_constraints import MinLength, MaxLength, LengthInterval
from data_generation_tool.errors import UnsatisfiableConstraints
from data_generation_tool.generators import ColumnGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Email


class EmailGenerator(ColumnGenerator):
    """
    Generator used for email values.

    We define the language for valid emails using the grammar : `<email> ::= <local_part>@<domain_part>.`.

    The domain part contains at least one dot, so we can write it as
    `<domain_part> ::= <first_part>.<second_part>`
    where `first_part` and `second_part` are nonempty.

    Notes :
        The constraints Regex, AllowedWords, ForbiddenWords, MinWords, MaxWords and WordsInterval are ignored
    """

    def generate(self, column: ColumnGenerationRequest, count: int) -> list:
        if column.column_type != Email:
            raise ValueError(f"Column type {column.column_type} is not Email")

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

        if min_len is not None and min_len < 6:
            raise UnsatisfiableConstraints("The minimum length should be at least 7 for a valid email address to be "
                                           "generated")

        if min_len is None:
            min_len = 8

        if max_len is None:
            max_len = 20

        values = []
        for _ in range(count):
            length_researched = self.rng.integers(min_len, max_len, endpoint=True) - 1
            domain_ending = self.rng.choice([x for x in _domain_endings if len(x) <= length_researched - 3])
            remaining_len = length_researched - len(domain_ending)
            first_part_len = self.rng.integers(1, remaining_len - 2, endpoint=True)
            second_part_len = remaining_len - first_part_len

            first_part = self._generate_random_string(first_part_len)
            second_part = self._generate_random_string(second_part_len)

            email = first_part + '@' + second_part + domain_ending
            values.append(email)

        return self.post_processing(values, column.constraints)

    def _generate_random_string(self, n: int) -> str:
        chars = list(string.ascii_letters + string.digits)
        return ''.join(self.rng.choice(chars) for _ in range(n))


# Some random tlds that will be used to generate random emails
_domain_endings = [
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
