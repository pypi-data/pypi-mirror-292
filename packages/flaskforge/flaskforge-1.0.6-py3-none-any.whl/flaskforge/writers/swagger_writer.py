import inspect

from inflect import engine
from stringcase import pascalcase
from .base_writer import AbstractWriter


class SwaggerWriter(AbstractWriter):
    """
    Generates and writes Swagger (OpenAPI) documentation for API resources.

    The `SwaggerWriter` class creates Swagger documentation files for the resources
    defined in the API. It uses the Flask-APISpec library to generate documentation based
    on the methods and schemas of the resource classes.

    Attributes:
        type (str): The type of writer, set to "document".
        model (str): The name of the model for which documentation is being generated.
    """

    type = "document"

    def __init__(self, args: object, **kwargs):
        """
        Initialize the SwaggerWriter with model details.

        Args:
            args (object): Arguments object containing model details.
            **kwargs: Additional keyword arguments.

        TODO:
            - Validate `args` to ensure it contains the required attributes.
            - Handle cases where `kwargs` might not contain the expected keys.
        """
        self.args = args
        self.model = self.args.model
        self.set_writable()
        self.set_writable_path("documents")

    def write_source(self):
        """
        Write the source code for the Swagger documentation.

        Returns:
            None if only the model is required; otherwise, writes the source code.

        TODO:
            - Implement additional checks or logging if needed.
            - Ensure that the file writing operation is handled correctly.
        """
        return None if self.is_model_only() else super().write_source()

    def get_source(self) -> str:
        """
        Generate the source code for the Swagger documentation based on the resource class.

        Returns:
            str: The formatted source code for the Swagger documentation.

        TODO:
            - Enhance the method to handle more complex scenarios or customizations.
            - Validate that the generated documentation meets API specification requirements.
        """

        p = engine()

        ResourceClass = self.get_class(
            "resource",
            f"{pascalcase(self.model if self.args.name is None else self.args.name)}",
        )
        members = inspect.getmembers(ResourceClass, predicate=inspect.isfunction)

        exclude_timestamp = """("created_at", "updated_at")"""
        exclude = """("id", "created_at", "updated_at")"""
        only_ = self.args.only if hasattr(self.args, "only") else []
        only_ = [f"""'{only}'""" for only in only_ if only_]
        only = f"""only=({",".join(only_)})""" if only_ else None

        source_import = f"""
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc

from utils.helper import get_query_class

from schemas import {pascalcase(self.model)}Schema

{pascalcase(self.model)}Query = get_query_class({pascalcase(self.model)}Schema)
"""

        source_class = f"""
class {self.classname}(MethodResource):
    __endpoint__ = "{p.plural(self.model if self.args.name is None else self.args.name)}"
    __blueprint__ = "{p.plural(self.model if self.args.name is None else self.args.name)}_route"
"""

        source_methods = [
            f"""
    @doc(tags=["{pascalcase(self.classname.replace("Resource", "").replace("Document", ""))}"])
    {'' if hasattr(self.args, "use_single") and self.args.use_single else f'''@use_kwargs(
    {
        pascalcase(self.model + "Query") if method == "get" else pascalcase(self.model) + "Schema"
    }{f'(exclude={exclude if method == "post" else exclude_timestamp})' if method != "get" and only is None else f"{f'({only})' if only is not None else ''}"},
    location=({"'query'" if method == "get" else "'json'"}))'''}
    def {method}(self): ...
"""
            for method, _ in members
            if not method.endswith("_request")
        ]

        source_method = "\n".join(source_methods)

        return self.format(source_import + source_class + source_method)
