import os

from inflect import engine
from stringcase import snakecase, pascalcase
from .base_writer import AbstractWriter


class RouteWriter(AbstractWriter):
    """
    Generates route files for a Flask API based on a given model.

    The `RouteWriter` class is responsible for creating route files that define
    the routing setup for a specific model in a Flask application. It generates
    the necessary source code including Blueprint setup and API resource registration.

    Attributes:
        type (str): The type of writer, set to "route".
        args (object): Arguments object containing model details.
        route (str): The name of the route based on the model.
        resource_classname (str): The name of the resource class associated with the route.
        route_name (str): The name of the route in snake_case.
        route_filename (str): The filename for the route.
    """

    type = "route"

    def __init__(self, args: object, **kwargs):
        """
        Initialize the RouteWriter with model details.

        Args:
            args (object): Arguments object containing model details.
            **kwargs: Additional keyword arguments.

        TODO:
            - Validate `args` to ensure it contains the required attributes.
            - Handle cases where `args.model` might be None or invalid.
        """
        self.args = args
        self.route = self.args.model if self.args.name is None else self.args.name
        p = engine()
        self.route_name = f"{p.plural(snakecase(self.route))}_route"
        self.resource_classname = f"{pascalcase(self.route)}Resource"
        self.route_filename = f"{self.route_name}.py"

    def write_source(self):
        """
        Write the generated route source code to the appropriate file.

        If `self.args.model_only` is True, this method will not perform any writing.

        TODO:
            - Implement error handling for file writing operations.
            - Ensure directory creation and file writing handle potential exceptions.
        """

        if self.is_model_only():
            return None

        ROUTE_PATH = f"{self.project_root}/routes"

        if not os.path.exists(ROUTE_PATH):
            os.makedirs(ROUTE_PATH)
            self.write(f"{ROUTE_PATH}/__init__.py")

        self.write(f"{ROUTE_PATH}/{self.route_filename}", self.get_source())
        self.write_module(ROUTE_PATH, cls=False)

    def get_source(self) -> str:
        """
        Generate the source code for the route file based on the model.

        Returns:
            str: The formatted source code for the route file.

        TODO:
            - Validate the generated source code to ensure correctness and completeness.
            - Handle cases where `self.resource_classname` might not be found or imported correctly.
        """
        api_name = f"{self.route}_api"

        source_code = f"""
from flask import Blueprint

from resources import {self.resource_classname}
from resources.base_resource import Api

{self.route_name} = Blueprint("{self.route_name}", __name__{
    f", url_prefix='/{self.args.url_prefix}'" if hasattr(self.args, "url_prefix") else ""
    })

{api_name} = Api({self.route_name})

{api_name}.add_resource(
    {self.resource_classname},
    {f"'/<{self.args.type}:{self.args.param}>'" 
    if hasattr(self.args, "use_single") and self.args.use_single 
    else f"f'/{{{self.resource_classname}.__endpoint__}}'"},
    endpoint={self.resource_classname}.__endpoint__
)
"""
        return self.format(source_code)
