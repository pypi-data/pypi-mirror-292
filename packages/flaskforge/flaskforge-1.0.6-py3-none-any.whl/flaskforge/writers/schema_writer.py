import ast

import astor
from inflect import engine
from stringcase import pascalcase, snakecase
from sqlalchemy.orm import class_mapper, ColumnProperty
from flaskforge.utils.commons import join_path
from flaskforge.modifiers import FieldModifier, ImportModifier
from .base_writer import AbstractWriter


class SchemaWriter(AbstractWriter):
    """
    Generates and writes schema files for SQLAlchemy models.

    The `SchemaWriter` class is responsible for creating schema files for the models
    defined in the SQLAlchemy ORM. It translates model attributes into Marshmallow fields
    and handles relationships between models.

    Attributes:
        type (str): The type of writer, set to "schema".
        fields (list): List of field definitions for the schema.
        relationship (str or None): Relationship strategy for nested schemas.
        child_model (str or None): Name of the child model for relationships.
        kwargs (dict): Additional keyword arguments.
        model (str): The name of the model.
        _type_map (dict): Mapping of SQLAlchemy types to Marshmallow fields.
        _validate (dict): Mapping of SQLAlchemy types to Marshmallow validation.
    """

    type = "schema"

    def __init__(self, args: object, **kwargs) -> None:
        """
        Initialize the SchemaWriter with model details.

        Args:
            args (object): Arguments object containing model details.
            **kwargs: Additional keyword arguments such as `strategy` and `child_model`.

        TODO:
            - Validate `args` to ensure it contains the required attributes.
            - Handle cases where `kwargs` might not contain the expected keys.
        """
        self.fields = []
        self.args = args
        self.kwargs = kwargs
        self.model = self.args.model

        self._type_map = {
            "str": "fields.Str",
            "text": "fields.Text",
            "int": "fields.Int",
            "bool": "fields.Bool",
            "bytes": "fields.Raw",
            "Decimal": "fields.Float",
            "datetime": "fields.DateTime",
        }
        self._validate = {"str": "validate.Length"}

        self.set_writable()

        self.set_writable_path("schemas")

    def write_nested(self):
        """
        Write a nested schema if a child model and relationship strategy are defined.

        Raises:
            ValueError: If `child_model` or `relationship` is not defined.

        TODO:
            - Implement error handling for file writing operations.
            - Ensure that the schema file is correctly formatted and written.
        """
        self.relationship = int(self.kwargs["strategy"])

        # Reverse child and parent model if belongto relationship
        self.model = (
            snakecase(self.kwargs["child_model"]).replace("_model", "")
            if self.relationship >= 4 and self.relationship <= 7
            else self.args.model
        )
        self.child = (
            pascalcase(f"{self.args.model}_model")
            if self.relationship >= 4 and self.relationship <= 7
            else self.kwargs["child_model"]
        )

        self.only_relationship = self.relationship in (1, 3, 5, 7)

        self.set_writable()
        self.set_writable_path("schemas")

        self.child = snakecase(self.child.replace("Model", ""))
        schema_source = self.get_source()
        schema_class = pascalcase(f"{self.child}_schema")
        many = int(self.relationship) not in [0, 1, 4, 5]
        field_source = f"""{engine().plural(self.child) if many else self.child} = fields.Nested({schema_class}, many={many}{
            ", required=True, allow_none=False" if self.only_relationship else ""})"""

        tree = ast.parse(schema_source)
        tree = FieldModifier(field_source).visit(tree)
        tree = ImportModifier(f"from .{self.child}_schema import {schema_class}").visit(
            tree
        )
        formatted_source = self.format(astor.to_source(tree))

        self.write(join_path(self.writable_path, self.filename), formatted_source)

    def get_source(self) -> str:
        """
        Generate the source code for the schema based on the SQLAlchemy model.

        Returns:
            str: The formatted source code for the schema.

        TODO:
            - Enhance type mapping to handle additional SQLAlchemy types.
            - Validate the model's attributes and handle potential exceptions.
        """
        ModelClass = self.get_class("model", self.model)
        mapper = class_mapper(ModelClass)

        for attr in mapper.attrs:
            # skip none sqlalchemy fields
            if not isinstance(attr, ColumnProperty):
                continue

            (column,) = attr.columns
            express = "{required}{attribute}{validate}".format(
                required=(
                    ""
                    if column.nullable
                    else f"required=True, allow_none={column.nullable},"
                ),
                attribute=(
                    "" if attr.key == column.name else f"attribute='{attr.key}',"
                ),
                validate=(
                    f"""validate=validate.Length(max={column.type.length}),"""
                    if column.type.python_type.__name__ == "str"
                    and hasattr(column.type, "length")
                    else ""
                ),
            )
            self.fields.append(
                f"""\t{column.name} = {self._type_map[column.type.python_type.__name__]}"""
                f"""({express if express else ""})"""
            )

        source_import = """
from marshmallow import fields, validate

from .base_schema import BaseSchema
"""

        source_class = f"class {self.classname}(BaseSchema):\n"
        source_field = "\n".join(self.fields)
        source_code = source_import + source_class + source_field

        return self.format(source_code)
