import os
from inflect import engine
from stringcase import snakecase, pascalcase

from .base_writer import AbstractWriter


class ResourceWriter(AbstractWriter):
    """
    Generates resource classes for a Flask API based on a given model.

    The `ResourceWriter` class is responsible for creating Flask resource classes
    that define endpoints and methods for CRUD operations. It generates the necessary
    source code including imports, class definitions, and method implementations
    based on the specified model and endpoints.

    Attributes:
        type (str): The type of writer, set to "resource".
        args (object): Arguments object containing model details and endpoint configurations.
        model (str): The snake_case version of the model name.
        model_methods (tuple): A tuple of methods to be included in the resource class.
    """

    type = "resource"

    def __init__(self, args: object, **kwargs):
        """
        Initialize the ResourceWriter with model and endpoint details.

        Args:
            args (object): Arguments object containing model details and endpoint configurations.
            **kwargs: Additional keyword arguments.

        TODO:
            - Validate `args` to ensure it contains the required attributes.
            - Handle cases where `args.endpoints` or `args.exclude_endpoints` might be None or invalid.
        """

        self.args = args
        default_methods = ("get", "post", "put", "patch", "delete")
        self.mapped_method = {
            "get": (
                f"""{"search" if hasattr(self.args, "use_search") 
                and self.args.use_search else "get_all"}"""
                if hasattr(self.args, "use_single") and not self.args.use_single
                else "get"
            ),
            "post": "add",
            "delete": "delete",
            "put": "update",
            "patch": "update",
        }

        self.model = snakecase(self.args.model)
        self.name = self.args.name if hasattr(self.args, "name") else self.model

        self.model_methods = (
            self.args.endpoints
            if hasattr(self.args, "endpoints") and self.args.endpoints
            else (
                list(
                    filter(
                        lambda e: e not in self.args.exclude_endpoints,
                        default_methods,
                    )
                )
                if hasattr(self.args, "exclude_endpoints")
                and self.args.exclude_endpoints
                else default_methods
            )
        )

        self.set_writable()

        self.set_writable_path("resources")

    def write_source(self):
        """
        Write the generated resource source code to the appropriate file.

        If `self.args.model_only` is True, this method will not perform any writing.

        TODO:
            - Implement error handling for file writing operations.
        """

        return None if self.is_model_only() else super().write_source()

    def get_source(self) -> str:
        """
        Generate the source code for the resource class based on the model and endpoints.

        Returns:
            str: The formatted source code for the resource class.

        TODO:
            - Validate the generated source code to ensure correctness and completeness.
            - Handle cases where the `self.model_methods` might result in empty or invalid source code.
        """

        p = engine()

        endpoint = route = p.plural(
            self.args.name if self.args.name is not None else self.args.model
        )

        source_import = f"""
from flask import make_response

from utils.helper import validator, authenticate
from schemas import {pascalcase(f"{self.model}_schema")}
from models import {pascalcase(f"{self.model}_model")}
from .base_resource import BaseResource
"""

        source_decorator = [
            f""""{method}": [validator({pascalcase(f"{self.model}_schema")
            }{",partial=True" if method in ["get", "patch"] else ""
              }{",exclude=('id',)" if method == "post" else ""}){",authenticate"}]"""
            for method in self.model_methods
        ]

        source_class = f"""
class {self.classname}(BaseResource):
    __endpoint__ = "{endpoint}"
    __blueprint__ = "{route}_route"

    model = {pascalcase(f"{self.model}_model")}
    model.Schema_ = {pascalcase(f"{self.model}_schema")}

    method_decorators = {{{",".join(source_decorator)}}}
"""
        source_methods = [
            f"""
    def {method}(self, {
                "expression: dict = dict(), pagination: dict = dict()"
                if method == "get" else "schema: dict = dict()"
            }):

        model = self.model({"schema" if method != "get" else ""})
        model.{self.mapped_method[method]}({f"{'expression, pagination' if hasattr(self.args, 'use_single') and not self.args.use_single else 'expression'}" if method == "get" else ""})
        
        return make_response(model.jsonify(), {
            200 if method not in ["post", "delete"] else (201 if method == "post" else 204)
            })
"""
            for method in self.model_methods
        ]

        source_method = "\n".join(source_methods)

        full_source = source_import + source_class + source_method

        return self.format(full_source)
