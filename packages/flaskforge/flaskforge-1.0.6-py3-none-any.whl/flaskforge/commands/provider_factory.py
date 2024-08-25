from .initapp_provider import InitappProvider
from .create_provider import CreateProvider
from .create_resource_provider import CreateResourceProvider
from .create_authentication_provider import CreateAuthentication


class ProviderFactory:
    """
    Factory class for creating and retrieving provider instances based on the specified type.

    TODO:
        - Implement validation for the provided `name` to handle cases where the provider type is not found.
        - Add logging to track which provider was instantiated and its associated operations.
        - Consider adding support for additional provider types in the future.
        - Provide a mechanism to handle initialization failures or exceptions when instantiating providers.
    """

    provider = {
        "create": CreateProvider,
        "initapp": InitappProvider,
        "create:authentication": CreateAuthentication,
        "create:resource": CreateResourceProvider,
    }

    def __new__(cls, name: str):
        """
        Instantiates and returns the handler method of the specified provider.

        Args:
            name (str): The type of provider to instantiate (e.g., "create" or "initapp").

        Returns:
            Callable: The handler method of the instantiated provider.

        TODO:
            - Validate `name` to ensure it corresponds to a valid provider type.
            - Add error handling to manage cases where the provider instantiation fails.
            - Implement unit tests to ensure correct behavior of the factory method.
        """
        provider = cls.provider.get(name)
        if not provider:
            raise ValueError(
                f"Provider type '{name}' is not recognized."
            )  # Handle invalid provider type

        provider_ = provider()
        return provider_.handler
