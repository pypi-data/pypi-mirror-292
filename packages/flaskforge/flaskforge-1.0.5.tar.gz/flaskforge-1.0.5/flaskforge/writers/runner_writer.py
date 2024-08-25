import os
from stringcase import snakecase
from flaskforge.utils.commons import join_path
from .base_writer import AbstractWriter


class RunnerWriter(AbstractWriter):
    """
    Generates and writes the runner script for a Flask project.

    The `RunnerWriter` class is responsible for creating the `runner.py` file,
    which serves as the entry point for running the Flask application. It copies
    the content from a base runner file and writes it to the project's runner script.

    Attributes:
        type (str): The type of writer, set to "runner".
        args (object): Arguments object containing project details.
        project (str): The name of the project.
        runner (str): Path to the runner script.
        base_runner (str): Path to the base runner script template.
    """

    type = "runner"

    def __init__(self, args: object, **kwargs):
        """
        Initialize the RunnerWriter with project details.

        Args:
            args (object): Arguments object containing project details.
            **kwargs: Additional keyword arguments.

        TODO:
            - Validate `args` to ensure it contains the required attributes.
            - Handle cases where `args.project` might be None or invalid.
        """
        self.args = args
        self.project = self.args.project

        self.runner = join_path(self.project_root, self.project, "runner.py")
        self.base_runner = join_path(self.package_root, "bases", "base_runner.py")

    def validate_project(self, project: str) -> str:
        """
        Validate and format the project name.

        Args:
            project (str): The project name.

        Returns:
            str: The formatted project name in snake_case.

        TODO:
            - Enhance validation to handle more complex cases.
            - Handle cases where `project` might be an empty string or invalid.
        """
        return snakecase(project) if project != "." else ""

    def write_source(self):
        """
        Write the generated runner source code to the runner file.

        Raises:
            ValueError: If the runner file already exists.

        TODO:
            - Implement error handling for file writing operations.
            - Ensure that file creation and writing handle potential exceptions.
        """

        if not self.args.force and os.path.isfile(self.runner):
            raise ValueError(
                "runner.py is already exists. Use --force to overwrite the existing"
            )

        self.write(self.runner, self.get_source())

    def get_source(self) -> str:
        """
        Read and format the source code from the base runner template.

        Returns:
            str: The formatted source code for the runner script.

        TODO:
            - Validate the source code to ensure it meets project requirements.
            - Handle cases where the base runner file might not be found or readable.
        """
        with open(self.base_runner) as reader:
            source_code = reader.read()

        return self.format(source_code)
