import os
import sys
import ast
from abc import ABC, abstractmethod

import astor
from black import FileMode, format_str
from stringcase import pascalcase, snakecase

from flaskforge.modifiers import AssignmentModifier
from flaskforge.utils.commons import dirname, join_path


class AbstractWriter(ABC):
    """
    Abstract base class for file writers in the project.

    Attributes:
        fields (list): List of fields to be included in the generated files.
        project_root (str): Root directory of the project.
        package_root (str): Root directory of the package.
    """

    fields = []
    project_root = os.getcwd()
    package_root = dirname(__file__, 2)
    source_code = None

    def set_writable(self, name=None):
        """
        Set the class name and filename based on the model and type.

        This method sets the `classname` to PascalCase and `filename` to snake_case.

        TODO:
            - Add error handling for invalid or missing `model` or `type`.
            - Ensure `model` and `type` are properly validated before usage.
        """

        self.args.name = name

        self.classname = (
            pascalcase(f"{self.args.name}_resource")
            if name is not None
            else pascalcase(f"{self.model}_{self.type}")
        )

        self.filename = f"""{snakecase(f"{self.classname}")}.py"""

    def set_writable_path(self, dir: str):
        """
        Set the path where files will be written.

        Args:
            dir (str): Directory path to set as writable.

        TODO:
            - Validate `dir` to ensure it is a valid directory path.
            - Handle cases where `dir` is an invalid path or contains special characters.
        """
        self.writable_path = join_path(self.project_root, dir)

    def set_source(self, source: str) -> None:
        self.source_code = self.format(source)

    def is_model_only(self) -> bool:
        """
        Check if the writer is operating in model-only mode.

        Returns:
            bool: True if model_only is set, False otherwise.

        TODO:
            - Ensure `args.model_only` is properly handled and documented.
            - Add validation to check if `args` is an appropriate object.
        """
        return hasattr(self.args, "model_only") and self.args.model_only

    def write_source(self):
        """
        Write the source files to the writable path.

        Creates the directory if it does not exist, writes base files if they exist,
        and writes the main source file and module imports.

        TODO:
            - Add error handling for file operations, such as permission issues or file not found errors.
            - Refactor into smaller methods for improved readability and maintainability.
            - Implement logging to track the writing process and potential issues.
        """
        if not os.path.exists(self.writable_path):
            os.makedirs(self.writable_path)

            self.write(join_path(self.writable_path, "__init__.py"))

            # Write base file if it exists
            base_path = join_path(self.package_root, "bases", f"base_{self.type}.py")

            # overwrite use_docker to true once dockerfile exist
            setattr(
                self.args,
                "use_docker",
                os.path.isfile(join_path(self.project_root, "Dockerfile")),
            )

            if os.path.isfile(base_path):
                with open(base_path, "r") as reader:
                    base_model = reader.read()

                if (
                    hasattr(self.args, "use_docker")
                    and not self.args.use_docker
                    and self.type == "model"
                ):
                    engine_source = """create_engine(
                    environ.get("DATABASE_URL", "sqlite:///storage.db"))"""

                    session_source = """scoped_session(
                    sessionmaker(bind=engine,query_cls=BaseQuery))"""
                    tree = ast.parse(base_model)
                    tree = AssignmentModifier("engine", engine_source.strip()).visit(
                        tree
                    )
                    tree = AssignmentModifier("session", session_source.strip()).visit(
                        tree
                    )
                    base_model = astor.to_source(tree)

                self.write(
                    join_path(self.writable_path, f"base_{self.type}.py"),
                    self.format(base_model),
                )

            # raise Exception

        # Write the main source file
        self.write(
            join_path(self.writable_path, self.filename),
            self.get_source() if self.source_code is None else self.source_code,
        )
        self.write_module(self.writable_path)

    @abstractmethod
    def get_source(self) -> str:
        """
        Abstract method to get the source code.

        Subclasses must implement this method to return the source code as a string.

        TODO:
            - Ensure subclasses handle all necessary aspects of source code generation.
            - Validate the format and structure of the generated source code.
        """
        pass

    def format(self, source: str) -> str:
        """
        Format the source code using the Black code formatter.

        Args:
            source (str): Source code to format.

        Returns:
            str: Formatted source code.

        TODO:
            - Consider allowing configuration of formatter options.
            - Handle cases where formatting might fail or produce errors.
        """
        return format_str(source, mode=FileMode())

    def read(self, file_path: str = None):
        with open(
            (
                join_path(self.writable_path, self.filename)
                if file_path is None
                else file_path
            ),
            "r",
        ) as reader:
            source = reader.read()

        return source

    def write(self, file_path: str, source: str = ""):
        """
        Write the given source code to a file.

        Args:
            file_path (str): Path of the file to write to.
            source (str): Source code to write to the file.

        TODO:
            - Add error handling for file write operations.
            - Implement logging to track file write operations and issues.
        """
        with open(file_path, "w") as writer:
            writer.write(source)

    def write_module(self, module_path: str, cls: bool = True):
        """
        Write module imports and `__all__` to the `__init__.py` file.

        Args:
            module_path (str): Path to the module directory.
            cls (bool): Whether to use PascalCase for class imports.

        TODO:
            - Validate module file names and handle naming conflicts.
            - Refactor to handle different module structures and file types.
        """
        modules = [
            file.replace(".py", "")
            for file in os.listdir(module_path)
            if os.path.isfile(join_path(module_path, file)) and file != "__init__.py"
        ]

        module_imports = "\n".join(
            [
                f"from .{file} import {pascalcase(file) if cls else file}"
                for file in modules
            ]
        )

        module_all = f"\n\n__all__ = {[(pascalcase(file) if cls and not file.startswith('base_') else file) for file in modules if not file.startswith('base_')]}"

        self.write(join_path(module_path, "__init__.py"), module_imports + module_all)

    def get_field_source(self, attr: dict) -> str:
        """
        Generate source code for fields from attribute dictionary.

        Args:
            attr (dict): Dictionary of attributes to generate source code for.

        Returns:
            str: Generated field source code.

        TODO:
            - Validate `attr` to ensure it contains expected field builders.
            - Handle edge cases where attributes may not have the `string_field` attribute.
        """
        return f"\t{','.join([builder.string_field for builder in attr.values()])})".replace(
            "(,", "("
        )

    def get_fields_source(self) -> str:
        """
        Generate source code for all fields.

        Returns:
            str: Generated source code for all fields.

        TODO:
            - Validate the `fields` list to ensure it contains expected attributes.
            - Handle cases where `fields` might be empty or contain unexpected values.
        """
        return "\n".join([self.get_field_source(field) for field in self.fields])

    def get_class(self, module: str, cls_name: str):
        """
        Import and retrieve a class from a module.

        Args:
            module (str): Name of the module.
            cls_name (str): Name of the class.

        Returns:
            type: The retrieved class.

        TODO:
            - Handle potential import errors and module not found issues.
            - Ensure the class is correctly retrieved and validate its existence.
            - Consider using more explicit import methods if dynamic imports become complex.
        """
        if self.project_root not in sys.path:
            sys.path.append(self.project_root)

        cls = pascalcase(f"{cls_name}_{module}")
        import_ = __import__(
            f"{module}s.{snakecase(f'{cls_name}_{module}')}", fromlist=[""]
        )
        return getattr(import_, cls)
