from stringcase import pascalcase
from .base_writer import AbstractWriter


class ModelWriter(AbstractWriter):
    """
    A writer for generating SQLAlchemy model files.

    This class inherits from `AbstractWriter` and is responsible for creating
    and writing SQLAlchemy model files based on the provided fields and model name.

    Attributes:
        type (str): The type of writer, set to "model".
    """

    type = "model"

    def __init__(self, args: str, **kwargs) -> None:
        """
        Initialize the ModelWriter with model-specific details.

        Args:
            args (str): Arguments object containing model details.
            **kwargs: Additional keyword arguments containing fields.

        TODO:
            - Validate the `args` and `kwargs` to ensure they contain necessary attributes.
            - Handle cases where `fields` might be missing or improperly formatted.
        """
        self.args = args
        self.fields = kwargs.get("fields", [])
        self.model = self.args.model
        self.set_writable()
        self.set_writable_path("models")

    def get_source(self) -> str:
        """
        Generate the source code for the SQLAlchemy model.

        Constructs the import statements, class definition, table name, and field attributes
        for the SQLAlchemy model. Formats the generated source code before returning it.

        Returns:
            str: The formatted source code for the model.

        TODO:
            - Handle cases where `fields` might be empty or improperly formatted.
            - Improve import handling to avoid collisions or redundant imports.
            - Add error handling for cases where the base model import might fail.
            - Consider using a more robust method for handling dynamic imports or field types.
        """
        # Generate import statements for columns and related types
        source_import = "from sqlalchemy import Column, " + ", ".join(
            set(
                [
                    pascalcase(v.prop[1])
                    for field in self.fields
                    for k, v in field.items()
                    if v.type_ == "obj"
                ]
            )
        )

        # Import statement for base model
        source_relate_import = "from .base_model import BaseModel"

        # Class definition and table name
        source_class = f"class {self.classname}(BaseModel):\n"
        source_table_name = f"\t__tablename__ = '{self.model}'\n\n"

        # Field attributes
        source_attr = self.get_fields_source()

        # Combine all parts into final source code
        source_code = (
            f"{source_import}\n\n"
            + f"{source_relate_import}\n\n"
            + source_class
            + source_table_name
            + source_attr
        )

        # Format and return the source code
        formatted_code = self.format(source_code)
        return formatted_code
