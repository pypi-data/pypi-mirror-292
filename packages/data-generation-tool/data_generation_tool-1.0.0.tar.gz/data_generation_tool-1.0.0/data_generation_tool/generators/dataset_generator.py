import pandas as pd
from fmkforml.makers.fairmaker import get_most_fair_test_dt

from data_generation_tool.generators import *
from data_generation_tool.requests import GenerationRequest
from data_generation_tool.types import *


class DatasetGenerator:
    """
    Class to handle dataset generation
    """

    def __init__(self, random_state: int | None = None):
        self.random_state = random_state

    def generate_data(self, request: GenerationRequest) -> pd.DataFrame:
        """
        From a query containing the details about the details of a dataset, generate a full dataset

        Note that when fairness involved for at least one column, the count is not guaranteed to be followed

        Parameters
        ----------
        request : GenerationRequest
            The data for generating each column
        Returns
        -------
        df
            A pandas dataframe containing the generated dataset
        """

        columns = request.columns
        generator_factory = GeneratorFactory()
        generated_columns = {}
        fair_columns_index = []
        for column in columns:
            if column.fair:
                fair_columns_index.append(columns.index(column))
            generator = generator_factory.generator(column.column_type, self.random_state)
            column_data = generator.generate(column, request.count)
            generated_columns[column.name] = column_data

        if fair_columns_index:
            generated_columns = get_most_fair_test_dt(pd.DataFrame(generated_columns), coef=0.25, columns=fair_columns_index)
        else:
            generated_columns = pd.DataFrame(generated_columns)
        return generated_columns


class GeneratorFactory:
    """
    Util class to help retrieving the needed generator for a type
    """

    def __init__(self):
        self.generators = {
            Numeric: NumberGenerator,
            Integer: IntegerGenerator,
            Float: FloatGenerator,
            Text: TextGenerator,
            Email: EmailGenerator,
            URL: URLGenerator,
            E164PhoneNumber: E164PhoneNumberGenerator,
            Name: NameGenerator,
            Date: DateGenerator,
            Country: CountryGenerator,
            City: CityGenerator,
            Meal: MealGenerator,
            Fruit: FruitGenerator,
            Condiment: CondimentGenerator,
            Drink: DrinkGenerator,
            Brand: BrandGenerator,
            Scent: ScentGenerator,
            Quality: QualityGenerator,
            Feeling: Feeling,
            Movie: MovieGenerator,
            Series: SeriesGenerator,
            Object: ObjectGenerator,
            Channel: ChannelGenerator,
            App: AppGenerator,
            Book: BookGenerator,
            Website: WebsiteGenerator,
            SocialNetwork: SocialNetworkGenerator,
            Job: JobGenerator,
            Enum: EnumGenerator
        }

    def generator(self, column_type: type, random_state: int | None):
        """
        Returns a generator instance for the given column type. If the column type is 'Any',
        it randomly selects and returns an instance of one of the available generators.

        Args:
            column_type (type) : The type of column for which a generator is required.
            random_state (int | None) : Parameter for reproductible results


        Returns:
            An instance of the appropriate generator class.

        Raises:
            ValueError: If no generator is available for the given column type.
        """

        rng = np.random.default_rng(random_state)

        if column_type == Any:
            generator_class = rng.choice(list(self.generators.values()))
            return generator_class()
        elif column_type in self.generators:
            return self.generators[column_type](random_state)
        else:
            raise ValueError(f"No generator available for type: {column_type}")
