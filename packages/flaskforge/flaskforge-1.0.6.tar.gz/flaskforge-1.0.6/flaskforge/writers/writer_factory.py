from flaskforge.writers import (
    ModelWriter,
    RouteWriter,
    SchemaWriter,
    ResourceWriter,
    SwaggerWriter,
    RegisterWriter,
    AppWriter,
    RunnerWriter,
    RelationshipWriter,
    HelperWriter,
    MigrationWriter,
)


class WriterFactory:
    """
    Factory class for creating instances of various writer types.

    The `WriterFactory` class provides a way to create instances of different writer
    classes based on the provided factory type. It maps factory types to corresponding
    writer classes and initializes them with the provided arguments.

    Attributes:
        writer (dict): A dictionary mapping writer types to their corresponding classes.
    """

    writer = {
        "model": ModelWriter,
        "route": RouteWriter,
        "schema": SchemaWriter,
        "resource": ResourceWriter,
        "swagger": SwaggerWriter,
        "app": AppWriter,
        "runner": RunnerWriter,
        "register": RegisterWriter,
        "relationship": RelationshipWriter,
        "helper": HelperWriter,
        "migration": MigrationWriter,
    }

    def __new__(cls, factory: str, args: object, **kwargs):
        """
        Create and return an instance of the specified writer class.

        Args:
            factory (str): The type of writer to create (e.g., "model", "route").
            args (object): The arguments to initialize the writer class.
            **kwargs: Additional keyword arguments to initialize the writer class.

        Returns:
            An instance of the corresponding writer class.

        Raises:
            ValueError: If the specified factory type is not found in the `writer` dictionary.

        TODO:
            - Implement error handling if the `factory` type is not found in the `writer` dictionary.
            - Consider adding logging for the creation of writer instances.
            - Enhance validation of `args` and `kwargs` before initializing the writer.
        """
        writer_class = cls.writer.get(factory)

        if writer_class is None:
            raise ValueError(f"Writer type '{factory}' is not recognized.")

        return writer_class(args, **kwargs)
