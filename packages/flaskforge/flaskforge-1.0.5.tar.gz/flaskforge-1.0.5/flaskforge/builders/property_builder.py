from stringcase import pascalcase
from flaskforge.utils.exception import InvalidAttr
from .base_builder import AbstractBuilder


class PropertyBuilder(AbstractBuilder):
    """Builds property definitions based on a string input.

    Attributes:
        type_ (str): The type identifier for the property. Defaults to "prop".
        prop (tuple): A tuple parsed from the input string.
        string_field (str): The formatted property definition string.
    """

    type_ = "prop"

    def __init__(self, data: str) -> None:
        """
        Initializes the PropertyBuilder with a data string.

        Args:
            data (str): The input string containing the property information.
        """
        self.prop = self.parse_tuple(data)
        self.string_field = ""

    def build(self) -> str:
        """
        Builds the property definition string based on the parsed property.

        Returns:
            str: The key extracted from the property data.

        Raises:
            InvalidAttr: If the property is not a valid key-value pair or if the key is not valid.
        """
        if not self._is_valid_prop():
            raise InvalidAttr(
                "Property argument is not key-value paired or has an invalid format."
            )

        key, value = self.prop
        available = self.get_arguments(self.type_)

        if key not in available:
            raise InvalidAttr(f"{key} is not a valid property key.")

        self.string_field = f"{key}={pascalcase(value)}"
        return key

    def _is_valid_prop(self) -> bool:
        """
        Checks if the parsed property is a valid key-value pair.

        Returns:
            bool: True if the property is valid, False otherwise.
        """
        return len(self.prop) == 2

    # TODO:
    # 1. Ensure that `parse_tuple` and `get_arguments` methods from `AbstractBuilder` are correctly implemented and documented.
    # 2. Implement unit tests to verify the behavior of `PropertyBuilder` with various input scenarios.
    # 3. Verify that `InvalidAttr` is the appropriate exception for this context, or consider defining a more specific exception if needed.
