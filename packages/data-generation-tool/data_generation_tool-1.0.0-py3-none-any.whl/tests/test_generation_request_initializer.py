import pytest

from data_generation_tool.constraints.column_constraints import Prime, MinLength, Positive, AllowedWords
from data_generation_tool.constraints.dataset_constraints import NoneOf, AtLeast
from data_generation_tool.requests import GenerationRequest, ColumnGenerationRequest
from data_generation_tool.types import Numeric, Email, Integer, Text


class TestGenerationRequestInitializer:
    def test_gen_request_with_nothing(self):
        with pytest.raises(ValueError) as _:
            _ = GenerationRequest(columns=[], count=5)

    def test_gen_request_with_duplicate_columns(self):
        with pytest.raises(ValueError) as _:
            _ = GenerationRequest(
                columns=[
                    ColumnGenerationRequest(
                        column_type=Numeric,
                        name="Foo",
                    ),
                    ColumnGenerationRequest(
                        column_type=Email,
                        name="Foo",
                    )
                ],
                count=5
            )

    def test_gen_request_with_correct_values(self):
        _ = GenerationRequest(
            columns=[
                ColumnGenerationRequest(
                    column_type=Numeric,
                    name="Foo",
                ),
                ColumnGenerationRequest(
                    column_type=Email,
                    name="Bar",
                )
            ],
            count=5
        )

        assert 1 == 1

    def test_gen_request_with_invalid_count(self):
        with pytest.raises(ValueError) as _:
            _ = GenerationRequest(
                columns=[
                    ColumnGenerationRequest(
                        column_type=Numeric,
                        name="Foo",
                    ),
                    ColumnGenerationRequest(
                        column_type=Email,
                        name="Bar",
                    )
                ],
                count=0
            )

    def test_gen_request_with_dataset_constraints_for_non_existing_columns(self):
        with pytest.raises(ValueError) as _:
            _ = GenerationRequest(
                columns=[
                    ColumnGenerationRequest(
                        column_type=Numeric,
                        name="Foo",
                    ),
                    ColumnGenerationRequest(
                        column_type=Email,
                        name="Bar",
                    )
                ],
                constraints=[
                    NoneOf({
                        "Whoami": Prime()
                    })
                ],
                count=5
            )

    def test_gen_request_with_dataset_constraints_with_mismatched_type(self):
        with pytest.raises(ValueError) as _:
            _ = GenerationRequest(
                columns=[
                    ColumnGenerationRequest(
                        column_type=Numeric,
                        name="Foo",
                    ),
                    ColumnGenerationRequest(
                        column_type=Email,
                        name="Whoami",
                    )
                ],
                constraints=[
                    NoneOf({
                        "Whoami": Prime()
                    })
                ],
                count=5
            )

    def test_gen_request_with_dataset_constraint_matching_type(self):
        _ = GenerationRequest(
            columns=[
                ColumnGenerationRequest(
                    column_type=Numeric,
                    name="Foo",
                ),
                ColumnGenerationRequest(
                    column_type=Integer,
                    name="Whoami",
                )
            ],
            constraints=[
                NoneOf({
                    "Whoami": Prime()
                })
            ],
            count=5
        )

        assert 1 == 1

    def test_gen_request_with_multiple_dataset_constraints_matching_type(self):
        _ = GenerationRequest(
            columns=[
                ColumnGenerationRequest(
                    column_type=Text,
                    name="Foo",
                ),
                ColumnGenerationRequest(
                    column_type=Integer,
                    name="Whoami",
                )
            ],
            constraints=[
                NoneOf({
                    "Whoami": Prime(),
                    "Foo": MinLength(10)
                }),
                AtLeast(columns_and_constraints={
                    "Whoami": Positive(),
                    "Foo": AllowedWords(['friare', 'africa'])
                }, count=4)
            ],
            count=5
        )

        assert 1 == 1
