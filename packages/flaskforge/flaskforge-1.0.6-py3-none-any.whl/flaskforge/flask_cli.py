import argparse
from flaskforge.commands.provider_factory import ProviderFactory


class FlaskCli:
    """
    Singleton class for managing Flask CLI tools.
    """

    _instance = None
    provider = ProviderFactory

    def __new__(cls, *args, **kwargs):
        """
        Ensure only one instance of FlaskCli is created (singleton pattern).

        Returns:
            FlaskCli: The singleton instance of FlaskCli.
        """
        if not cls._instance:
            cls._instance = super(FlaskCli, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the FlaskCli instance. Set up argument parsing and command storage.

        TODO:
            - Add error handling for initialization failures.
        """
        if not hasattr(self, "initialized"):
            self.initialized = True
            # Initialize the argument parser
            self.parser = argparse.ArgumentParser(
                description="Artisan CLI tool for creating Flask resources"
            )
            # Create subparsers for different commands
            self.sub_parser = self.parser.add_subparsers(
                dest="command", help="Available commands"
            )
            self.command = {}

    def init(self):
        """
        Parse command-line arguments and execute the corresponding command function.

        TODO:
            - Implement error handling for unknown commands and invalid arguments.
            - Add logging to capture command execution details and errors.
        """
        args = self.parser.parse_args()
        if args.command in self.command:
            # Call the function associated with the command
            self.command[args.command]["function"](args)
        else:
            # Print help if command is not recognized
            self.parser.print_help()

    def create_command(self, name: str, help: str):
        """
        Register a new command with the CLI tool.

        Args:
            name (str): The name of the command.
            help (str): A brief description of the command.

        TODO:
            - Add support for command aliases.
            - Validate that the command name is unique.
        """
        # Create a parser for the new command
        command_parser = self.sub_parser.add_parser(name, help=help)
        # Register the command function using the provider
        command_function = self.provider(name)
        self.command[name] = {
            "parser": command_parser,
            "function": command_function,
        }

    def add_argument(self, command: str, name: str, *args, **kwargs):
        """
        Add an argument to a specified command's parser.

        Args:
            command (str): The name of the command to which the argument should be added.
            name (str): The name of the argument. For optional arguments, should start with '--'.
            *args: Positional arguments for argparse.add_argument().
            **kwargs: Keyword arguments for argparse.add_argument().

        TODO:
            - Validate argument configurations to ensure they are correctly set up.
            - Implement support for dynamically adding or removing arguments.
        """
        parser = self.command[command]["parser"]

        parser.add_argument(name, *args, **kwargs)
