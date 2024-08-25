import os
from abc import ABC, abstractmethod

from flaskforge.utils.io import StandardIO
from flaskforge.utils.argument import Argument

class AbstractProvider(ABC):
    """
    Abstract base class for providers that handle specific functionalities.

    This class defines the common interface and shared methods for all provider classes.
    Concrete implementations must override the `handler` method to provide specific
    functionality.

    Attributes:
        AVAILABLE_ARGS (dict): A dictionary of available arguments converted from `Argument`.
        project_path (str): The path to the current working directory.
        io (StandardIO): An instance of `StandardIO` for handling input/output operations.
    """

    AVAILABLE_ARGS = Argument.to_dict()
    project_path = os.getcwd()
    io = StandardIO()

    def get_field_str(self, attr: dict) -> str:
        """
        Generate a formatted string for fields based on the provided attributes.

        Args:
            attr (dict): A dictionary of field attributes where each value has a `string_field` property.

        Returns:
            str: A formatted string representing the fields.

        TODO:
            - Verify that all dictionary values have the `string_field` attribute.
            - Add error handling for unexpected attribute formats or missing properties.
        """
        return f"""\t{
            ",".join([builder.string_field for builder in attr.values()])
            })\n""".replace(
            "(,", "("
        )

    @abstractmethod
    def handler(self, args: object):
        """
        Abstract method for handling specific functionality.

        Args:
            args (object): The arguments to process.

        This method must be overridden by concrete implementations to provide specific
        handling logic based on the arguments provided.

        TODO:
            - Define the expected format and structure of `args`.
            - Add validation for `args` to ensure it meets the expected criteria.
        """
        pass
