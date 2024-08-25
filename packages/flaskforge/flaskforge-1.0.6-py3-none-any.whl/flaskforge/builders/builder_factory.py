from flaskforge.utils.argument import Argument
from flaskforge.utils.exception import InvalidAttr, OkExit, KoExit, DoneExit, HintExit
from . import AttributeBuilder, PropertyBuilder, ObjectBuilder


class BuilderFactory:
    """Factory class for creating builders based on input data.

    Attributes:
        builders (tuple): Tuple of builder classes available for instantiation.
        exits (dict): Dictionary mapping exit strings to exit exceptions.
        data (str): The input data string used to determine the builder.
        available_args (dict): Dictionary of available arguments.
        key (str): The key extracted from the input data.
        opt (dict): Options associated with the extracted key.
    """

    builders = (AttributeBuilder, PropertyBuilder, ObjectBuilder)
    available_args = Argument.to_dict()

    hint_msg = f"""
    The arguments are key-value-paired or name, property, value.

    Example:

        attr username

            - attr: the model class attribute
            - username: the name of model class to be create

        type string 30

            - type: the of the username attribute
            - string:   Python data type mapped with sqlalchemy
            - 30:    the length of the string data type

        nullable false

    NOTE: available arguments - {", ".join(available_args.keys())}
"""
    exits = {"ok": OkExit, "ko": KoExit, "done": DoneExit, "hint": HintExit(hint_msg)}

    def __init__(self, data: str) -> None:
        """
        Initializes the BuilderFactory with a data string.

        Args:
            data (str): The input data string.
        """
        self.data = data.strip()

        self.check_exit()
        self.set_options()

    def get_builder(self):
        """
        Retrieves the appropriate builder class based on the options.

        Returns:
            AbstractBuilder: An instance of the builder class corresponding to the data type.
        """
        BuilderClass = next(b for b in self.builders if b.type_ == self.opt.get("type"))
        return BuilderClass(self.data)

    def set_options(self):
        """
        Sets the options for the builder based on the input data.

        Raises:
            InvalidAttr: If the key extracted from the data is not a valid attribute.
        """
        try:
            key = self.data.split(" ")[0]
            opt = self.available_args[key]
        except KeyError:
            raise InvalidAttr(f"{key} is an invalid attribute")

        self.key = key
        self.opt = opt

    def check_exit(self):
        """
        Checks if the input data matches any exit condition and raises the corresponding exception.

        Raises:
            OkExit: If the data matches the "ok" exit condition.
            KoExit: If the data matches the "ko" exit condition.
            DoneExit: If the data matches the "done" exit condition.
        """
        if self.data in self.exits:
            raise self.exits[self.data]

    # TODO:
    # 1. Ensure that the `Argument.to_dict()` method is correctly implemented and returns the expected dictionary of arguments.
    # 2. Implement unit tests to verify that `BuilderFactory` behaves as expected with various input data.
    # 3. Consider adding more detailed error handling or logging if necessary to improve debugging and maintenance.
