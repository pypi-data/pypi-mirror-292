from typing import Callable

from simplepyds.Errors.CustomErrors import ContainerEmptyError
from simplepyds.LinkedList.DoublyLinkedList import DoublyLinkedList
from simplepyds.LinkedList.Node import DoublyLinkedNode
from simplepyds.Base.Container import Container


class HashTable[T](Container):
    def __init__(
            self,
            length: int,
            auto_grow: bool = False,
            grow_factor: float = 1.5,
            hash_function: Callable[[T], int] | None = None
    ) -> None:
        """
        Initialize the hash table.
        :param length: The length of the hash table.
        :param auto_grow: Whether the hash table is automatically growing or not.
        :param grow_factor: The growing factor of the hash table.
        :param hash_function: The optional hash function to use.
        """
        super().__init__()
        self.container = [DoublyLinkedList() for _ in range(length)]
        self._length: int = len(self.container)
        self._inserted_count: int = 0
        self._type: type | None = None
        self.auto_grow: bool = auto_grow
        self.grow_factor = grow_factor
        self._hash_function = hash_function

    def __hash_function(self, value: T) -> int:
        """
        Gets the hash value of a given value.
        :param value: The value to hash.
        :return: The hash value of a given value.
        """
        if self._hash_function is not None:
            return self._hash_function(value)

        key = hash(value)
        return key % self._length

    @staticmethod
    def get_value(dll_node: DoublyLinkedNode) -> T:
        """
        Gets the value of a given node.
        :param dll_node: The node to get the value from.
        :return: The value of a given node.
        """
        if dll_node is not None:
            return dll_node.value

    def increase_capacity(self) -> None:
        """
        Increases the capacity of the hash table.
        :return: None
        """
        new_length = round(self._length * self.grow_factor)
        new_container = [DoublyLinkedList() for _ in range(new_length)]
        values: list[T] = []
        for dll in self.container:
            if dll.is_empty():
                continue
            else:
                contents = dll.foreach(self.get_value, node=True)
                for content in contents:
                    values.append(content)
        self.container = new_container
        self._length = len(self.container)
        for _ in values:
            self.insert(_)

    def insert(self, value: T) -> None:
        """
        Inserts a new value into the hash table.
        :param value: The value to insert.
        :return:
        """
        self._check_type(value)
        hash_value = self.__hash_function(value)
        self.container[hash_value].insert_back(value)
        self._inserted_count += 1

        if self.auto_grow:
            if self.load_factor() >= 0.7:
                self.increase_capacity()

    def delete(self, value: T) -> None:
        """
        Deletes a value from the hash table.
        :param value: The value to delete.
        :return: None
        """
        if self.is_empty():
            raise ContainerEmptyError("Hashing Table")

        self._check_type(value)

        hash_value = self.__hash_function(value)
        self.container[hash_value].delete(value, all_occurrences=True)

    def search(self, value: T) -> bool:
        """
        Checks if a given value is in the hash table.
        :param value: The value to search.
        :return: True if the value exists in the hash table, False otherwise.
        """
        self._check_type(value)
        hash_value = self.__hash_function(value)
        return self.container[hash_value].contains(value)

    def length(self) -> int:
        """
        Gets the length of the hash table.
        :return: The length of the hash table.
        """
        return self._length

    def inserted_count(self) -> int:
        """
        Gets the number of values added to the hash table.
        :return: The number of values added to the hash table.
        """
        return self._inserted_count

    def load_factor(self) -> float:
        """
        Gets the factor of the hash table.
        :return: The factor of the hash table.
        """
        return self._inserted_count / self._length

    def is_empty(self):
        """
        Checks if the hash table is empty.
        :return: True if the hash table is empty, False otherwise.
        """
        return self._inserted_count == 0

    def __str__(self) -> str:
        """
        Gets the string representation of the hash table.
        :return: The string representation of the hash table.
        """
        string = "["
        for dll in self.container:
            string += f"{dll}, "
        string = string.rstrip(", ")
        string += "]"
        return string
