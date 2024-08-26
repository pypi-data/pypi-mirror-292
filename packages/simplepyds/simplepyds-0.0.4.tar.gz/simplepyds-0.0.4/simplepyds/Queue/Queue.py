from typing import Callable, Any, List
from simplepyds.Base import Container
from simplepyds.Errors import ContainerEmptyError
from simplepyds.LinkedList import DoublyLinkedList


class Queue[T](Container):
    def __init__(self) -> None:
        """
        Initialize the Queue.
        """
        super().__init__()
        self._container = DoublyLinkedList()

    def length(self) -> int:
        """
        Return the length of the Queue.
        :return: The length of the Queue.
        """
        return self._container.length

    def enqueue(self, value: T) -> None:
        """
        Add a value to the Queue.
        :param value: The value to add.
        :return: None
        """
        self._check_type(value)
        self._container.insert_back(value)

    def dequeue(self) -> None:
        """
        Remove a value from the Queue.
        :return: None
        """
        if not self.is_empty():
            self._container.delete_front()
        else:
            raise ContainerEmptyError("Queue")

    def peek(self) -> T | None:
        """
        Return the value at the front of the Queue.
        :return: The value at the front of the Queue or `None`.
        """
        if not self.is_empty():
            return self._container.head.value
        return None

    def is_empty(self) -> bool:
        """
        Check if the Queue is empty.
        :return: True if the Queue is empty, False otherwise.
        """
        return self._container.is_empty()

    def __str__(self) -> str:
        """
        Return a string representation of the Queue.
        :return: String representation of the Queue.
        """
        string = "["
        for _ in self._container:
            string += f"{_}, "
        string = string.rstrip(", ")
        string += "]"
        return string

    def foreach(self, fn: Callable[[T], Any]) -> None | List[Any]:
        """
        Apply a function to each element of the Queue.
        :param fn: The function to apply to each element.
        :return: The list of elements after applying the function or `None`.
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
        Return the next element in the Queue.
        :return: The next element in the Queue.
        """
        return self._container.__next__()

    def __iter__(self) -> "Queue[T]":
        """
        Iterate over the Queue.
        :return: The Queue.
        """
        return self

    def clear(self) -> None:
        """
        Remove all elements from the Queue.
        :return: None
        """
        self._container.clear()
