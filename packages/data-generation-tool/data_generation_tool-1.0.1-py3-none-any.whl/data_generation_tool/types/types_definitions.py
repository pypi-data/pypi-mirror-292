class Any:
    """
    Placeholder type to identify all columns.
    """
    pass


class Numeric(Any):
    """
    Placeholder type to identify numeric columns.
    """
    pass


class Integer(Numeric):
    """
    Placeholder type to identify integer columns.
    """
    pass


class Float(Numeric):
    """
    Placeholder type to identify floating point columns.
    """
    pass


class Text(Any):
    """
    Placeholder type to identify text columns.
    """
    pass


class Email(Text):
    """
    Represents an email address.
    """
    pass


class URL(Text):
    """
    Represents a Uniform Resource Locator (URL).
    """
    pass


class E164PhoneNumber(Text):
    """
    Represents an E.164 formatted phone number.
    """
    pass


class Name(Text):
    """
    Represents a person's name.
    """
    pass


class Date(Any):
    """
    Placeholder type to identify date columns.
    """
    pass


class Enum(Any):
    """
    Placeholder type to identify enum columns.
    """
    pass


class Country(Enum):
    """
    Represents a country name.
    """
    pass


class City(Enum):
    """
    Represents a city name.
    """
    pass


class Meal(Enum):
    """
    Represents a meal name.
    """
    pass


class Fruit(Enum):
    """
    Represents a fruit name.
    """
    pass


class Condiment(Enum):
    """
    Represents a condiment name.
    """
    pass


class Drink(Enum):
    """
    Represents a drink name.
    """
    pass


class Brand(Enum):
    """
    Represents a brand name.
    """
    pass


class Scent(Enum):
    """
    Represents a scent name.
    """
    pass


class Quality(Enum):
    """
    Represents a quality name.
    """
    pass


class Feeling(Enum):
    """
    Represents a feeling name.
    """
    pass


class Movie(Enum):
    """
    Represents a movie name.
    """
    pass


class Series(Enum):
    """
    Represents a series name.
    """
    pass


class Object(Enum):
    """
    Represents an object name.
    """
    pass

class Book(Enum):
    """
    Represents a channel name.
    """
    pass

class Channel(Enum):
    """
    Represents a channel name.
    """
    pass


class App(Enum):
    """
    Represents an app name.
    """
    pass


class Website(Enum):
    """
    Represents a website name.
    """
    pass


class SocialNetwork(Enum):
    """
    Represents a social network name.
    """
    pass


class Job(Enum):
    """
    Represents a job name.
    """
    pass
