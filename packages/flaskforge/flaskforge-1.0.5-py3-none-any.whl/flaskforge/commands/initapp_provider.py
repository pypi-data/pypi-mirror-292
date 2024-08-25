import os

from flaskforge.writers.writer_factory import WriterFactory
from flaskforge.utils.commons import exec_command, join_path

from .base_cli_provider import AbstractProvider


class InitappProvider(AbstractProvider):
    """
    Handles the initialization of application components including app setup, helper scripts, and runner configuration.

    TODO:
        - Add functionality to customize app initialization based on project type or configuration.
        - Implement a verification step to check for existing configurations or files before creating new ones.
        - Provide options for generating configuration files or templates based on user inputs or predefined settings.
        - Enhance error handling for file operations and writer processes.
    """

    def handler(self, args: object):
        """
        Manages the creation of essential application components and displays success message.

        Args:
            args (object): Command-line arguments.

        TODO:
            - Add user prompts for additional configurations or options during initialization.
            - Implement logging to track the initialization process and any issues encountered.
            - Consider adding a feature to rollback or clean up in case of initialization failures.
        """

        try:

            if exec_command("git --version")[:11] != "git version":
                raise Exception(
                    f"""FlaskForge cannot find any source version control!"""
                )

            self.args = args

            writers = ["app", "helper", "runner"]

            _ = [WriterFactory(writer, args).write_source() for writer in writers]

            os.chdir(f"./{self.args.project}")
            exec_command("git init")
            exec_command("git add .")
            exec_command("git commit --message 'Initial commit'")

            # self.io.clear()
            self.io.success(
                f"""Your app has been created successfully.\n\t{
                    f"cd {self.args.project} and " if self.args.project != "." else ""
                    }python runner.py in your terminal to start"""
            )

        except Exception as err:
            self.io.error(err)
