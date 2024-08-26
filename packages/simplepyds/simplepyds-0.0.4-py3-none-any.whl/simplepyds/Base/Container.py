from typing import Any


class Container:
    def __init__(self):
        self._type = None

    def _check_type(self, value: Any):
        """
        Checks if a given value is the correct type
        :param value: A value to be checked
        :return: None
        :raises TypeError: If the value is not of the correct type
        """
        if self._type is None:
            self._type = type(value)
        else:
            if not isinstance(value, self._type):
                raise TypeError(f"'{value}' is not of type {self._type}")

    def is_empty(self):
        raise NotImplementedError("Base 'is_empty' method used. Please implement this method.")
