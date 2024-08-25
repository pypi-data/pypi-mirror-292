import ast
import astor

from flaskforge.utils.commons import join_path
from flaskforge.modifiers import CodeModifier, ImportModifier
from .base_writer import AbstractWriter


class RegisterWriter(AbstractWriter):
    """
    A writer for generating and updating the registration code in the runner file.

    This class inherits from `AbstractWriter` and is responsible for updating the `runner.py`
    file with auto-generated import statements and code to register blueprints and Swagger documents.

    Attributes:
        type (str): The type of writer, set to "register".
    """

    type = "register"

    def __init__(self, args: object, **kwargs) -> None:
        """
        Initialize the RegisterWriter with project-specific details.

        Args:
            args (object): Arguments object containing project details.
            **kwargs: Additional keyword arguments.

        TODO:
            - Validate the `args` object to ensure it contains necessary attributes.
            - Handle cases where `runner.py` might be missing or inaccessible.
        """
        self.args = args
        self.runner = join_path(self.project_root, "runner.py")

    def write_source(self):
        """
        Write the updated source code to the runner file.

        If the writer is operating in model-only mode, no changes are made. Otherwise,
        the runner file is updated with the generated source code.

        Returns:
            None: No return value if operating in model-only mode.

        TODO:
            - Implement error handling for file write operations.
            - Consider adding logging to track the writing process.
        """
        if not self.is_model_only():
            self.write(self.runner, self.get_source())

    def get_source(self) -> str:
        """
        Generate the updated source code for the runner file.

        This method reads the original source from the `runner.py` file, adds auto-generated
        import statements, and includes code to register blueprints and Swagger documents.

        Returns:
            str: The formatted source code with added imports and registration code.

        TODO:
            - Handle cases where `runner.py` might be missing or inaccessible.
            - Improve the robustness of import and code modifications to handle different file structures.
            - Validate the modifications to ensure they do not conflict with existing code.
        """
        with open(self.runner, "r") as file:
            original_source = file.read()

        # Define auto-generated import statements
        source_import = """
# Auto-generated import
from flask import Blueprint
from flask_apispec.views import MethodResourceMeta

from app import spec
from routes import *
from documents import *
"""

        # Define code to register blueprints and Swagger documents
        route_register_source = """
global_ = globals()

# Register all blueprints
_ = [app.register_blueprint(route) for route in global_.values() if isinstance(route, Blueprint)]

# Register all Swagger documents
_ = [spec.register(doc, blueprint=doc.__blueprint__, endpoint=doc.__endpoint__) for doc in global_.values() if isinstance(doc, MethodResourceMeta)]
"""

        # Parse and modify the original source code
        tree = ast.parse(original_source)
        tree = ImportModifier(source_import).visit(tree)
        tree = CodeModifier(route_register_source).visit(tree)
        formatted_source = astor.to_source(tree)

        return self.format(formatted_source)
