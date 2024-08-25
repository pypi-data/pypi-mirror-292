from stringcase import pascalcase
from flaskforge.utils.exception import InvalidAttr
from .base_builder import AbstractBuilder


class ObjectBuilder(AbstractBuilder):
    """Builds object definitions based on a string input.

    Attributes:
        type_ (str): The type identifier for the object. Defaults to "obj".
        prop (tuple): A tuple parsed from the input string.
        string_field (str): The formatted object definition string.
    """

    type_ = "obj"

    def __init__(self, data: str) -> None:
        """
        Initializes the ObjectBuilder with a data string.

        Args:
            data (str): The input string containing the object information.
        """
        self.prop = self.parse_tuple(data)
        self.string_field = ""

    def write_type(self, prop: str, value: str) -> str:
        """
        Writes the type with an optional value.

        Args:
            prop (str): The property name.
            value (str): The optional value.

        Returns:
            str: The formatted type string.
        """
        return f"{pascalcase(prop)}({value})" if value else pascalcase(prop)

    def write_argument(self, prop: str, value: str) -> str:
        """
        Placeholder method for writing arguments.

        Args:
            prop (str): The property name.
            value (str): The optional value.

        Returns:
            str: Placeholder for argument string.
        """
        # Implement logic for writing arguments here if needed
        pass

    def build(self) -> str:
        """
        Builds the object definition string based on the parsed property.

        Returns:
            str: The attribute extracted from the object data.

        Raises:
            InvalidAttr: If the property does not conform to the expected format or has invalid components.
        """
        if not self._is_valid_prop():
            raise InvalidAttr(
                "Object argument should include attr, property, and optionally value, separated by space."
            )

        try:
            attr, prop, value = self.prop
        except ValueError:
            # Handle case where there is no value provided
            attr, prop = self.prop
            value = None

        self.string_field = (
            self.write_type(prop, value)
            if attr == "type"
            else self.write_argument(prop, value)
        )

        return attr

    def _is_valid_prop(self) -> bool:
        """
        Checks if the parsed property is valid (i.e., has 2 or 3 components).

        Returns:
            bool: True if the property is valid, False otherwise.
        """
        return 2 <= len(self.prop) <= 3

    # TODO:
    # 1. Ensure that `parse_tuple` method from `AbstractBuilder` is correctly implemented and documented.
    # 2. Implement logic in `write_argument` if needed.
    # 3. Implement unit tests to verify the behavior of `ObjectBuilder` with various input scenarios.
    # 4. Review the exception handling to ensure it covers all potential edge cases.
