import math
import re
import string

import exrex

from data_generation_tool.constraints.column_constraints import Regex, MinLength, MaxLength, LengthInterval, MinWords, \
    MaxWords, WordsInterval, AllowedWords, ForbiddenWords
from data_generation_tool.errors import UnsatisfiableConstraints
from data_generation_tool.generators.column_generator import ColumnGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Text


class TextGenerator(ColumnGenerator):
    """
    Generator used for text values
    Using a lorem ipsum base for the generation
    The `exrex` library (https://pypi.org/project/exrex) is used to handle regular expressions

    Notes :
        When using the flag regex, it is the only constraint considered, the other ones being ignored
    """

    def generate(self, column: ColumnGenerationRequest, count: int) -> list:
        if column.column_type != Text:
            raise ValueError(f"Column type {column.column_type} is not Text")

        # Keep track of all the constraints applied since they change the way the text will be generated
        regex = None
        min_len = None
        max_len = None
        min_word_count = None
        max_word_count = None
        allowed = None

        for constraint in column.constraints:
            if isinstance(constraint, Regex):
                regex = constraint.value

            elif isinstance(constraint, MinLength):
                min_len = constraint.value

            elif isinstance(constraint, MaxLength):
                max_len = constraint.value

            elif isinstance(constraint, LengthInterval):
                min_len = constraint.lower_bound
                max_len = constraint.upper_bound

            elif isinstance(constraint, MinWords):
                min_word_count = constraint.value

            elif isinstance(constraint, MaxWords):
                max_word_count = constraint.value

            elif isinstance(constraint, WordsInterval):
                min_word_count = constraint.lower_bound
                max_word_count = constraint.upper_bound

            elif isinstance(constraint, AllowedWords):
                allowed = constraint.value

            elif isinstance(constraint, ForbiddenWords):
                regex = self._generate_exclude_regex(constraint.value)

        # The number of words to generate
        # By default, the lower bound is between 1 and 5
        # And the upper bound is between 1 and 5
        if min_word_count is None:
            if max_word_count is None:
                min_word_count = self.rng.integers(1, 5, endpoint=True)
            else:
                min_word_count = self.rng.integers(1, max_word_count, endpoint=True)

        if max_word_count is None:
            max_word_count = self.rng.integers(min_word_count, min_word_count + 5, endpoint=True)

        if min_word_count > max_word_count:
            raise UnsatisfiableConstraints("The minimum number of words should be less than the maximum number of "
                                           "words")

        if min_len is not None and max_len is not None and min_len > max_len:
            raise UnsatisfiableConstraints("The minimum length should be less than the maximum length")

        # The generation itself
        # We generate random strings and when the length of the string is constrained,
        # we use a notion of budget which is the amount of chars missing or in excess in our string
        # If current length > max_expected_length, the budget is (current length - max_expected_length) and
        # is positive
        # Otherwise, if current length < min_expected_length, the budget is (current length - min_expected_length
        # and is positive
        values = []
        for _ in range(count):
            words_count = self.rng.integers(min_word_count, max_word_count, endpoint=True)

            if allowed is not None:
                words = []
                for _ in range(words_count):
                    words.append(self.rng.choice(allowed))
                candidate_string = ' '.join(words)

                budget = 0
                candidate_string_len = len(candidate_string)

                if min_len is not None and candidate_string_len < min_len:
                    budget = candidate_string_len - min_len

                if max_len is not None and candidate_string_len > max_len:
                    budget = candidate_string_len - max_len

                while budget != 0:
                    if budget < 0:
                        shortest_word = min(words, key=len)
                        shortest_word_len = len(shortest_word)
                        smallest_word_index = words.index(shortest_word)
                        filtered_words = [word for word in allowed if len(word) - shortest_word_len <= -1 * budget]

                        if filtered_words:
                            word_to_add = self.rng.choice(filtered_words)
                            words[smallest_word_index] = word_to_add
                            budget += len(word_to_add) - shortest_word_len
                        else:
                            raise UnsatisfiableConstraints("Length constraint not satisfiable given the allowed words")
                    else:
                        longest_word = max(words, key=len)
                        longest_word_len = len(longest_word)
                        longest_word_index = words.index(longest_word)
                        filtered_words = [word for word in allowed if len(word) < longest_word_len]

                        if filtered_words:
                            word_to_add = self.rng.choice(filtered_words)
                            words[longest_word_index] = word_to_add
                            budget -= longest_word_len - len(word_to_add)
                        else:
                            raise UnsatisfiableConstraints("Length constraint not satisfiable given the allowed words")

                    candidate_string = ' '.join(words)
            elif regex is not None:
                candidate_string = exrex.getone(regex)
            else:
                # Using lorem ipsum
                words = []
                for i in range(words_count):
                    word_group = _lorem_words[self.rng.integers(2, 14, endpoint=True)]
                    words.append(self.rng.choice(word_group))

                candidate_string = ' '.join(words)

                budget = 0
                candidate_string_len = len(candidate_string)

                if min_len is not None and candidate_string_len < min_len:
                    budget = candidate_string_len - min_len

                if max_len is not None and candidate_string_len > max_len:
                    budget = candidate_string_len - max_len

                while budget != 0:
                    chars_to_distribute_evenly = math.ceil(abs(budget) / len(words))

                    if budget < 0:
                        for i in range(len(words)):
                            if budget == 0:
                                break

                            if chars_to_distribute_evenly > abs(budget):
                                words[i] += self._generate_random_string(abs(budget))
                                budget = 0
                            else:
                                words[i] += self._generate_random_string(chars_to_distribute_evenly)
                                budget += chars_to_distribute_evenly
                    else:
                        for i in range(len(words)):
                            if budget == 0:
                                break

                            string_length = len(words[i])
                            max_chars_removable = max(0, string_length - 1)
                            max_chars_removable = min(chars_to_distribute_evenly, max_chars_removable)
                            words[i] = words[i][max_chars_removable:]
                            budget -= max_chars_removable

                    candidate_string = ' '.join(words)

            values.append(candidate_string)

        return self.post_processing(values, column.constraints)

    def _generate_random_string(self, n: int) -> str:
        chars = list(string.ascii_letters + string.digits)
        return ''.join(self.rng.choice(chars) for _ in range(n))

    @staticmethod
    def _generate_exclude_regex(words: list[str]):
        escaped_words = [re.escape(word) for word in words]
        pattern = '|'.join(escaped_words)
        return r'\\b(?:(?!{0})\\w)+\\b'.format(pattern)


# Small dictionary of common words found in the lorem ipsum text ordered by size
_lorem_words = {
    2: ['ut', 'ab', 'et', 'ut', 'et', 'Ut', 'ad', 'ut', 'ex', 'ea', 'in', 'ea'],
    3: ['Sed', 'sit', 'rem', 'sit', 'aut', 'aut', 'sed', 'eos', 'qui', 'est', 'qui', 'sit', 'sed', 'non', 'vel', 'eum',
        'qui', 'vel', 'qui', 'eum', 'quo'],
    4: ['unde', 'iste', 'ipsa', 'quae', 'illo', 'sunt', 'Nemo', 'enim', 'quia', 'odit', 'quia', 'quia', 'amet', 'quia',
        'eius', 'modi', 'enim', 'quis', 'nisi', 'Quis', 'iure', 'esse', 'quam'],
    5: ['omnis', 'natus', 'error', 'totam', 'eaque', 'quasi', 'vitae', 'dicta', 'ipsam', 'fugit', 'magni', 'sequi',
        'Neque', 'porro', 'ipsum', 'dolor', 'velit', 'ullam', 'autem', 'velit', 'nihil', 'illum', 'nulla'],
    6: ['beatae', 'labore', 'dolore', 'magnam', 'minima', 'veniam', 'fugiat'],
    7: ['aperiam', 'dolores', 'ratione', 'dolorem', 'numquam', 'tempora', 'aliquam', 'quaerat', 'nostrum', 'aliquid',
        'commodi', 'dolorem'],
    8: ['voluptas', 'quisquam', 'adipisci', 'incidunt', 'corporis', 'suscipit', 'voluptas', 'pariatur'],
    9: ['inventore', 'veritatis', 'nesciunt.', 'voluptate', 'molestiae'],
    10: ['voluptatem', 'doloremque', 'laudantium', 'architecto', 'explicabo.', 'voluptatem', 'aspernatur', 'voluptatem',
         'laboriosam'],
    11: ['accusantium', 'consectetur', 'voluptatem.', 'consequatur', 'consequatur'],
    12: ['perspiciatis', 'consequuntur'],
    13: ['reprehenderit'],
    14: ['exercitationem']
}
