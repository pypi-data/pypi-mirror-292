import os
import re
import sys


class StandardIO:
    """
    A utility class for handling terminal input/output with support for color coding and text formatting.
    """

    # Color attributes
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"  # Reset to default

    def clear(self):
        """Clear the terminal screen."""
        sys.stdout.flush()
        os.system("cls" if os.name == "nt" else "clear")

    def color(self, color: str, msg: str) -> str:
        """
        Apply the specified color to the message and reset color at the end.

        :param color: Color code to apply.
        :param msg: Message to color.
        :return: Colored message string.
        """
        return f"{color}{msg}{self.RESET}".strip()

    def print(self, msg: str, color: str = WHITE, start: str = "\n\t", end: str = ""):
        """
        Print a message with optional color and formatting.

        :param msg: Message to print.
        :param color: Color code to apply.
        :param start: Text to print before the message.
        :param end: Text to print after the message.
        """
        print(f"{start}{self.color(color, msg)}{end}")

    def remove_ansi_escape_codes(self, text: str) -> str:
        """
        Remove ANSI escape codes from a string.

        :param text: String potentially containing ANSI escape codes.
        :return: String with ANSI escape codes removed.
        """
        ansi_escape = re.compile(r"\x1b[^m]*m")
        return ansi_escape.sub("", text)

    def print_centered(self, msg: str, color: str = WHITE):
        """
        Print a message centered horizontally in the terminal with optional color.

        :param msg: Message to center and print.
        :param color: Optional color for the message.
        """
        # Get terminal size
        columns, _ = os.get_terminal_size()

        # Strip leading and trailing spaces and center the message
        msg = self.remove_ansi_escape_codes(msg)

        centered_msg = msg.center(columns)

        # Print the centered message with color if provided
        print(centered_msg)

    def error(self, msg: str, color: str = WHITE, start: str = "\n\t", end: str = ""):
        """
        Print an error message in red.

        :param msg: Message to print.
        :param color: Color code for the message text.
        :param start: Text to print before the message.
        :param end: Text to print after the message.
        """
        self.print(
            f"{start}{self.color(self.RED, 'ERROR:')} {self.color(color, msg)}{end}"
        )

    def warning(self, msg: str, color: str = WHITE, start: str = "\n\t", end: str = ""):
        """
        Print a warning message in yellow.

        :param msg: Message to print.
        :param color: Color code for the message text.
        :param start: Text to print before the message.
        :param end: Text to print after the message.
        """
        self.print(
            f"{start}{self.color(self.YELLOW, 'WARNING:')} {self.color(color, msg)}{end}"
        )

    def success(self, msg: str, color: str = WHITE, start: str = "\n\t", end: str = ""):
        """
        Print a success message in green.

        :param msg: Message to print.
        :param color: Color code for the message text.
        :param start: Text to print before the message.
        :param end: Text to print after the message.
        """
        self.print(
            f"{start}{self.color(self.GREEN, 'SUCCEED:')} {self.color(color, msg)}{end}"
        )

    def info(self, msg: str, color: str = WHITE, start: str = "\n\t", end: str = ""):
        """
        Print an informational message in cyan.

        :param msg: Message to print.
        :param color: Color code for the message text.
        :param start: Text to print before the message.
        :param end: Text to print after the message.
        """
        self.print(
            f"{start}{self.color(self.CYAN, 'INFO:')} {self.color(color, msg)}{end}"
        )

    def confirm(self, msg: str) -> str:
        """
        Prompt the user for confirmation with a yes/no question.

        :param msg: Question to ask.
        :return: User's response.
        """
        response = input(f"\n\t{msg} {self.color(self.CYAN, '<yes/no>')} ~~~> ")
        if response.lower() not in ["yes", "no"]:
            self.error(f"Invalid answer [{response}]. Only <yes/no> is accepted.")
            return self.confirm(msg)
        return response

    def print_choice(self, choices: list):
        """
        Print a list of choices with an index.

        :param choices: List of choices to print.
        """
        maxlength = max(len(choice) for choice in choices)
        for i, choice in enumerate(choices):
            self.print(
                f"{choice:<{maxlength}} {' '} {'~' * 40}> {self.color(self.CYAN, str(i))}"
            )

    def choice(self, max: int, min: int = 0) -> int:
        """
        Prompt the user to select a choice within a specified range.

        :param max: Upper bound of valid choices (exclusive).
        :param min: Lower bound of valid choices (inclusive).
        :return: Selected choice.
        """
        choice = input(f"\n\tEnter your choice ~~~> ")
        if not choice.isdigit() or not min <= int(choice) < max:
            self.error(
                f"{choice} is an incorrect choice. Please input a number from {min} to {max - 1}."
            )
            return self.choice(max, min)
        return int(choice)
