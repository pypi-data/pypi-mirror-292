import math

from data_generation_tool.constraints.column_constraints import MinLength, MaxLength, LengthInterval, MinWords, \
    MaxWords, WordsInterval
from data_generation_tool.errors import UnsatisfiableConstraints
from data_generation_tool.generators import ColumnGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Name


class NameGenerator(ColumnGenerator):
    """
    Generator used for names generation

    Notes :
        The constraints Regex, AllowedWords, ForbiddenWords and are ignored
    """

    def generate(self, column: ColumnGenerationRequest, count: int) -> list:
        if column.column_type != Name:
            raise ValueError(f"Column type {column.column_type} is not Name")

        min_len = None
        max_len = None
        min_word_count = None
        max_word_count = None

        for constraint in column.constraints:
            if isinstance(constraint, MinLength):
                min_len = constraint.value
                min_word_count = self._calculate_min_words(min_len)

            elif isinstance(constraint, MaxLength):
                max_len = constraint.value
                max_word_count = self._calculate_max_words(max_len)

            elif isinstance(constraint, LengthInterval):
                min_len = constraint.lower_bound
                max_len = constraint.upper_bound
                min_word_count = self._calculate_min_words(min_len)
                max_word_count = self._calculate_max_words(max_len)

            elif isinstance(constraint, MinWords):
                min_word_count = constraint.value

            elif isinstance(constraint, MaxWords):
                max_word_count = constraint.value

            elif isinstance(constraint, WordsInterval):
                min_word_count = constraint.lower_bound
                max_word_count = constraint.upper_bound

        # Checking constraints
        if min_len is not None and max_len is not None and min_len > max_len:
            raise UnsatisfiableConstraints("The minimum length should be less than the maximum length")

        if min_len is not None and min_len < 2:
            raise UnsatisfiableConstraints("The minimum length should be at least 2")

        if max_len is not None and max_len < 2:
            raise UnsatisfiableConstraints("The maximum length should be at least 2")

        # The number of parts of the name
        if min_word_count is None and max_word_count is None:
            min_word_count = 2
            max_word_count = 2
        elif max_word_count is None:
            max_word_count = min_word_count + 2
        elif min_word_count is None:
            min_word_count = max(max_word_count - 2, 2)

        if min_len is None and max_len is None:
            min_len = 7
            max_len = 12
        elif max_len is None:
            max_len = min_len + 2
        elif min_len is None:
            min_len = min(7, max_len - 5)

        values = []

        for _ in range(count):
            length = self.rng.integers(min_len, max_len, endpoint=True)

            if min_word_count == 2 and max_word_count == 2:
                first_part_len = self.rng.integers(2, length - 3, endpoint=True)
                second_part_len = length - 1 - first_part_len

                if first_part_len not in _names:
                    raise UnsatisfiableConstraints("The length related constraints could not be satisfied : Max ("
                                                   f"{max_len}) and Min({min_len})")

                if second_part_len not in _names:
                    raise UnsatisfiableConstraints("The length related constraints could not be satisfied : Max ("
                                                   f"{max_len}) and Min({min_len})")

                first_part = self.rng.choice(_names[first_part_len])
                second_part = self.rng.choice(_names[second_part_len])
                candidate_string = first_part + ' ' + second_part
            else:
                generated = False
                names = []

                for word_count_in_generated_name in range(min_word_count, max_word_count + 1):
                    if not generated:
                        for _ in range(word_count_in_generated_name):
                            size_per_word = (length + 1 - word_count_in_generated_name) // word_count_in_generated_name

                            if size_per_word not in _names:
                                continue

                            names = []
                            remaining = length

                            for _ in range(word_count_in_generated_name):
                                possible_size = min(size_per_word, remaining)
                                remaining -= possible_size - 1
                                names.append(self.rng.choice(_names[size_per_word]))
                                generated = True
                    else:
                        break

                if not generated:
                    raise UnsatisfiableConstraints("The word count constraint could not be satisfied")
                else:
                    candidate_string = ' '.join(names)

            values.append(candidate_string)

        return self.post_processing(values, column.constraints)

    @staticmethod
    def _calculate_max_words(total_space: int):
        if total_space < 2:
            return 0
        remaining_space = total_space - 2
        num_words = (remaining_space // 3) + 1
        return num_words

    @staticmethod
    def _calculate_min_words(total_space: int):
        max_word_length = 15
        if total_space < max_word_length:
            return 1

        remaining_space = total_space - max_word_length
        num_words = (remaining_space // (max_word_length + 1)) + 1
        return num_words


_names = {
    2: ['Al', 'Jo', 'Ed', 'Mo', 'Ty', 'Bo', 'Di', 'Lu', 'No', 'Li', 'Cy', 'Vi'],
    3: ['Tom', 'Ann', 'Sam', 'Sue', 'Ray', 'Ben', 'Eva', 'Tim', 'Amy', 'Ian', 'Leo', 'Eve', 'Mia', 'Jay', 'Doe', 'Joe'],
    4: ['John', 'Mary', 'Paul', 'Judy', 'Mark', 'Sara', 'Jack', 'Emma', 'Adam', 'Noah', 'Lily', 'Owen', 'Leah',
        'Nina'],
    5: ['Alice', 'James', 'David', 'Laura', 'Brian', 'Diana', 'Kevin', 'Nancy', 'Karen', 'Jason', 'Susan',
        'Emily', 'Megan', 'Chloe'],
    6: ['Oliver', 'Sophia', 'Daniel', 'Joshua', 'Lauren', 'Justin', 'Evelyn', 'Carter', 'Olivia'],
    7: ['Michael', 'Jessica', 'William', 'Abigail', 'Matthew', 'Madison', 'Anthony', 'Zachary'],
    8: ['Isabella', 'Benjamin', 'Jonathan', 'Victoria', 'Samantha', 'Emmanuel', 'Benjamin', 'Samantha',
        'Jonathan'],
    9: ['Alexander', 'Charlotte', 'Christian', 'Gabriella', 'Dominique', 'Sebastian', 'Catherine', 'Alexandra',
        'Nathaniel', 'Elizabeth', 'Frederick', 'Alexander', 'Gabrielle', 'Anastasia', 'Zachariah', 'Demetrius'],
    10: ['Bernadette', 'Maximilian', 'Alexandria', 'Evangeline'],
    11: ['Christopher', 'Christopher', 'Constantine', 'Benedictine', 'Maximiliano'],
    12: ['Michelangelo', 'Christabella'],
    13: ['MichealAngelo'],
    14: ['DavidAlexander'],
    15: ['Francois-Xavier']
}
