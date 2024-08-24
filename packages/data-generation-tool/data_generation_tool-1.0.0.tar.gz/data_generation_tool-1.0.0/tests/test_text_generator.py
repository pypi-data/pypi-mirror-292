import re

import pytest

from data_generation_tool.constraints.column_constraints import Interval, MinWords, MaxWords, WordsInterval, MinLength, \
    MaxLength, AllowedWords, Regex
from data_generation_tool.generators import TextGenerator
from data_generation_tool.requests import ColumnGenerationRequest
from data_generation_tool.types import Numeric, Text


class TestTextGenerator:
    def test_text_generator_generation_with_unsupported_column_type(self):
        with pytest.raises(ValueError) as _:
            _ = TextGenerator().generate(
                column=ColumnGenerationRequest(
                    column_type=Numeric,
                    name="Dummy",
                    constraints=[
                        Interval(100, 10)
                    ]
                ),
                count=4
            )

    def test_text_generation_without_constraints(self):
        data = TextGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Text,
                name="Foo",
                constraints=[]
            ),
            count=4
        )

        assert len(data) == 4

    def test_text_generation_with_min_word_count_constraint(self):
        data = TextGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Text,
                name="Foo",
                constraints=[
                    MinWords(4)
                ]
            ),
            count=4
        )

        assert len(data) == 4
        for datum in data:
            assert len(datum.split()) >= 4

    def test_text_generation_with_max_word_count_constraint(self):
        data = TextGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Text,
                name="Foo",
                constraints=[
                    MaxWords(4)
                ]
            ),
            count=4
        )

        assert len(data) == 4
        for datum in data:
            assert len(datum.split()) <= 4

    def test_text_generation_with_simulated_word_interval_constraint(self):
        data = TextGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Text,
                name="Foo",
                constraints=[
                    MinWords(2),
                    MaxWords(4)
                ]
            ),
            count=4
        )

        assert len(data) == 4
        for datum in data:
            assert 2 <= len(datum.split()) <= 4

    def test_text_generation_with_word_interval_constraint(self):
        data = TextGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Text,
                name="Foo",
                constraints=[
                    WordsInterval(lower_bound=2, upper_bound=4),
                ]
            ),
            count=4
        )

        assert len(data) == 4
        for datum in data:
            assert 2 <= len(datum.split()) <= 4

    def test_text_generation_with_min_length_constraint(self):
        data = TextGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Text,
                name="Foo",
                constraints=[
                    MinLength(40)
                ]
            ),
            count=4
        )

        assert len(data) == 4
        for datum in data:
            assert len(datum) >= 40

    def test_text_generation_with_max_length_constraint(self):
        data = TextGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Text,
                name="Foo",
                constraints=[
                    MaxLength(20)
                ]
            ),
            count=4
        )

        assert len(data) == 4
        for datum in data:
            assert len(datum) <= 20

    def test_text_generation_with_length_interval_constraint(self):
        data = TextGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Text,
                name="Foo",
                constraints=[
                    MaxLength(20),
                    MinLength(10),
                ]
            ),
            count=4
        )

        assert len(data) == 4
        for datum in data:
            assert 10 <= len(datum) <= 20

    def test_text_generation_with_allowed_words_constraint(self):
        allowed = ['here', 'are', 'the', 'allowed', 'words']
        data = TextGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Text,
                name="Foo",
                constraints=[
                    AllowedWords(value=allowed),
                ]
            ),
            count=4
        )

        assert len(data) == 4
        for datum in data:
            assert all(element in allowed for element in datum.split())

    def test_text_generation_with_regex_constraint(self):
        regex = r'This is (a (code|cake|test)|an (apple|elf|output))\.'
        data = TextGenerator().generate(
            column=ColumnGenerationRequest(
                column_type=Text,
                name="Foo",
                constraints=[
                    Regex(regex),
                ]
            ),
            count=4
        )

        assert len(data) == 4
        assert all(re.match(regex, element) for element in data)
