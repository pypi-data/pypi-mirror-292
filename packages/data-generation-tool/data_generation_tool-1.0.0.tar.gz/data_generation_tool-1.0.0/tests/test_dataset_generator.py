from data_generation_tool.constraints.column_constraints import Interval
from data_generation_tool.generators import DatasetGenerator
from data_generation_tool.requests import GenerationRequest, ColumnGenerationRequest
from data_generation_tool.types import Numeric, Name


class TestDatasetGenerator:
    def test_dataset_generation_with_single_column(self):
        request = GenerationRequest(
            columns=[
                ColumnGenerationRequest(
                    column_type=Numeric,
                    name="Age",
                    constraints=[Interval(1, 80)])
            ],
            count=4
        )

        generator = DatasetGenerator()
        data_generated = generator.generate_data(request)

        assert len(data_generated.columns) == 1
        assert len(data_generated) == 4

    def test_dataset_generation_with_multiple_columns(self):
        request = GenerationRequest(
            columns=[
                ColumnGenerationRequest(
                    column_type=Numeric,
                    name="Age",
                    constraints=[Interval(1, 80)]
                ),
                ColumnGenerationRequest(
                    column_type=Name,
                    name="Name"
                )
            ],
            count=10
        )

        generator = DatasetGenerator()
        data_generated = generator.generate_data(request)

        assert len(data_generated.columns) == 2
        assert len(data_generated) == 10

    def test_dataset_generation_with_multiple_columns_and_random_state(self):
        request = GenerationRequest(
            columns=[
                ColumnGenerationRequest(
                    column_type=Numeric,
                    name="Age",
                    constraints=[Interval(1, 80)]
                ),
                ColumnGenerationRequest(
                    column_type=Name,
                    name="Name"
                )
            ],
            count=10
        )

        generator = DatasetGenerator(random_state=2)
        first_generated_data = generator.generate_data(request)

        for _ in range(19):  # The data should not change
            data_generated = generator.generate_data(request)
            assert first_generated_data.equals(data_generated), "Generated data changed unexpectedly"
