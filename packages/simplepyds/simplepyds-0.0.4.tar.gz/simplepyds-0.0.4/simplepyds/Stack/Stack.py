from typing import Callable, Any, List
from simplepyds.Base import Container
from simplepyds.Errors.CustomErrors import ContainerEmptyError


class Stack[T](Container):

    def __init__(self) -> None:
        """
        Initialize the stack
        """
        super().__init__()
        self._container = []
        self.curr_index = 0

    def push(self, value: T) -> None:
        """
        Pushes a value onto the stack
        :param value: The value to push
        :return: None
        """
        self._check_type(value)
        self._container.insert(0, value)

    def length(self) -> int:
        """
        Returns the length of the stack
        :return: The length of the stack
        """
        return len(self._container)

    def pop(self) -> None:
        """
        Pops the last element from the stack
        :return: None
        """
        if not self.is_empty():
            self._container.pop(0)
        else:
            raise ContainerEmptyError("Stack")

    def peek(self) -> T | None:
        """
        Returns the first element from the stack (top of the stack)
        :return: The first element from the stack (top of the stack)
        """
        if not self.is_empty():
            return self._container[0]
        else:
            return None

    def is_empty(self):
        """
        Checks if the stack is empty
        :return: True if the stack is empty otherwise False
        """
        return len(self._container) == 0

    def __str__(self) -> str:
        """
        Returns the string representation of the stack
        :return: The string representation of the stack
        """
        string = "["
        for _ in self._container:
            string += f"{_}, "
        string = string.rstrip(", ")
        string += "]"
        return string

    def foreach(self, fn: Callable[[T], Any]) -> None | List[Any]:
        """
        Applies a function to each element in the stack
        :param fn: The function to be applied
        :return: The list of elements after applying the function or `None`
        """
        results = []
        for _ in self._container:
            res = fn(_)
            results.append(res)

        for _ in results:
            if _ is not None:
                return results

    def __next__(self) -> T:
        """
        Returns the next element in the stack
        :return: The next element in the stack
        """
        if not self.is_empty():
            if self.curr_index >= len(self._container):
                self.curr_index = 0
                raise StopIteration()
            value = self._container[self.curr_index]
            self.curr_index += 1
            return value

    def __iter__(self):
        """
        Iterates over the stack
        :return: The stack
        """
        return self

    def clear(self):
        """
        Clears the stack
        :return: None
        """
        self._container = []
