from abc import ABC, abstractmethod
from flaskforge.utils.argument import Argument


class AbstractBuilder(ABC):
    """Abstract base class for all builders.

    This class defines the basic structure and common functionalities
    for all builder classes. It requires implementing the `build` method
    and provides utility methods for parsing data and retrieving arguments.

    Methods:
        build: Abstract method that must be implemented by subclasses.
        parse_tuple: Converts a space-separated string into a tuple.
        get_arguments: Retrieves arguments of a specific type.
    """

    @abstractmethod
    def build(self):
        """
        Abstract method that should be implemented by subclasses.

        Subclasses must provide their specific implementation for building
        the object or property.
        """
        pass

    def parse_tuple(self, data: str) -> tuple:
        """
        Converts a space-separated string into a tuple.

        Args:
            data (str): The input string to be converted.

        Returns:
            tuple: A tuple containing the elements of the input string.
        """
        return tuple(data.strip().split(" "))

    def get_arguments(self, type_: str) -> dict:
        """
        Retrieves arguments of a specific type.

        Args:
            type_ (str): The type of arguments to retrieve.

        Returns:
            dict: A dictionary of arguments where each key corresponds to
                  an argument name and the value is a dictionary containing
                  argument details.
        """
        return {k: v for k, v in Argument.to_dict().items() if v.get("type") == type_}

    # TODO:
    # 1. Ensure that `Argument.to_dict()` method is correctly implemented and returns the expected dictionary of arguments.
    # 2. Verify that subclasses correctly implement the `build` method as expected.
