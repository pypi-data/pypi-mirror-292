import re
from flaskforge.utils.exception import InvalidAttr
from .base_builder import AbstractBuilder


class AttributeBuilder(AbstractBuilder):
    """Builds attributes for columns based on a string input.

    Attributes:
        type_ (str): The type identifier for the attribute. Defaults to "attr".
        prop (tuple): A tuple parsed from the input string.
        string_field (str): The formatted column definition string.
    """

    type_ = "attr"

    def __init__(self, data: str):
        """
        Initializes the AttributeBuilder with a data string.

        Args:
            data (str): The input string containing the attribute information.
        """
        self.prop = self.parse_tuple(data)
        self.string_field = ""

    def build(self) -> str:
        """
        Builds the column definition string based on the parsed property.

        Returns:
            str: The key extracted from the attribute data.

        Raises:
            InvalidAttr: If the property is not a valid key-value pair or does not match the expected type.
        """
        if not self._is_valid_prop():
            raise InvalidAttr(
                "Attribute argument is not key-value paired or has an incorrect type"
            )

        key, value = self.prop

        self.string_field = self._format_column_definition(value)
        return key

    def _is_valid_prop(self) -> bool:
        """
        Checks if the parsed property is a valid key-value pair and matches the expected type.

        Returns:
            bool: True if the property is valid, False otherwise.
        """
        return len(self.prop) == 2 and self.prop[0] == self.type_

    def _format_column_definition(self, value: str) -> str:
        """
        Formats the column definition string based on the value.

        Args:
            value (str): The attribute name.

        Returns:
            str: The formatted column definition string.
        """
        # Remove leading underscores from the attribute name if present
        cleaned_value = re.sub(r"^_+", "", value)

        # Determine the format based on whether the value starts with an underscore
        if value.startswith("_"):
            return f'{value} = Column("{cleaned_value}")'
        return f"{value} = Column("
