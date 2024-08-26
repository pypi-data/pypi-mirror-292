class ContainerEmptyError(Exception):
    def __init__(self, name: str) -> None:
        """
        Exception raised when a _container is empty.
        :param name: The name of the _container.
        """
        self.message = f"\nCannot perform action on empty _container: '{name}'."

    def __str__(self) -> str:
        return self.message
