import os
from flaskforge.utils.commons import join_path
from .base_writer import AbstractWriter


class AppWriter(AbstractWriter):
    """
    AppWriter is responsible for writing application source files to a specific project directory.

    Attributes:
        type (str): The type of writer, defaults to "app".
        args (object): Arguments containing project information.
        project (str): The name of the project.
        project_path (str): The path to the project directory.
        app_path (str): The path to the application directory within the project.
        base_app (str): The path to the base application source file.
    """

    type = "app"

    def __init__(self, args: object, **kwargs):
        """
        Initialize the AppWriter with project arguments and setup paths.

        Args:
            args (object): An object containing project-related arguments.
            **kwargs: Additional keyword arguments.
        """
        self.args = args
        self.project = args.project

        # Setup project and application paths
        self.project_path = join_path(self.project_root, self.project)
        self.app_path = join_path(self.project_path, "app")
        self.base_app = join_path(self.package_root, "bases", "base_app.py")

    def write_source(self):
        """
        Write the application source files to the project directory.

        This method creates the application directory if it does not exist,
        copies the base environment file to the project's root directory,
        and writes the application's initialization file and source code.
        """
        # Create application directory if it does not exist
        if not os.path.exists(self.app_path):
            os.makedirs(self.app_path)

            # Copy base environment file
            if hasattr(self.args, "use_docker") and not self.args.use_docker:
                base_env_path = join_path(self.package_root, "bases", "base_env.py")
                with open(base_env_path, "r") as reader:
                    env_content = reader.read()
                    self.write(join_path(self.project_path, "env.example"), env_content)

        # Write application source code
        init_file_path = join_path(self.app_path, "__init__.py")
        self.write(init_file_path, self.get_source())

    def get_source(self) -> str:
        """
        Retrieve the base application source code and format it.

        Returns:
            str: The formatted source code.
        """
        with open(self.base_app, "r") as reader:
            source_code = reader.read()

        return self.format(source_code)
