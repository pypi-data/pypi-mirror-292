from simplepyds.Base import Container
from simplepyds.Errors.CustomErrors import ContainerEmptyError
from simplepyds.LinkedList.Node import DoublyLinkedNode
from typing import Any, Callable, Literal


class DoublyLinkedList[T](Container):

    def __init__(self):
        """
        Initialize a DoublyLinkedList.
        """
        super().__init__()
        self.head: DoublyLinkedNode[T] | None = None
        self.tail: DoublyLinkedNode[T] | None = None
        self.curr: DoublyLinkedNode[T] | None = None
        self._type: type | None = None
        self.length: int = 0
        self.__last_insert: Literal["front", "back"] = "front"

    def insert_front(self, value: T) -> None:
        """
        Inserts the value at the front of the list
        :param value: The value to be inserted
        :return: None
        """
        self._check_type(value)
        if self.is_empty():
            self.head = DoublyLinkedNode(value)
            self.tail = self.head
        else:
            old_head = self.head
            self.head = DoublyLinkedNode(value, _next=old_head)
            old_head.prev = self.head

        self.__last_insert = "front"
        self.length += 1

    def insert_back(self, value: T) -> None:
        """
        Inserts the value at the back of the list
        :param value: The value to be inserted
        :return: None
        """
        self._check_type(value)
        if self.is_empty():
            self.head = DoublyLinkedNode(value)
            self.tail = self.head
        else:
            old_tail = self.tail
            self.tail = DoublyLinkedNode(value)
            old_tail.next = self.tail

        self.__last_insert = "back"
        self.length += 1

    def delete_front(self) -> None:
        """
        Deletes the value at the front of the list
        :return: None
        """
        if self.is_empty():
            raise ContainerEmptyError("Doubly Linked List")

        if self.length == 1:
            self.head = None
            self.tail = None
            self.curr = None
            self.length = 0
            return

        old_head = self.head
        self.head = old_head.next
        self.head.prev = None

        self.length -= 1

    def delete_back(self) -> None:
        """
        Deletes the value at the back of the list
        :return: None
        """
        if self.is_empty():
            raise ContainerEmptyError("Doubly Linked List")

        if self.length == 1:
            self.head = None
            self.tail = None
            self.curr = None
            self.length = 0
            return

        old_tail = self.tail
        self.tail = old_tail.prev
        self.tail.next = None

        self.length -= 1

    def is_empty(self) -> bool:
        """
        Checks if the list is empty
        :return: True if the list is empty otherwise False
        """
        return True if self.head is None else False

    def next(self) -> None:
        """
        Moves the cursor to the next node.
        Changes the position of the cursor
        :return: None
        """
        if self.curr is None:
            self.curr = self.head
        else:
            self.curr = self.curr.next

    def previous(self) -> None:
        """
        Moves the cursor to the previous node
        Changes the position of the cursor
        :return: None
        """
        if self.curr is None:
            self.curr = self.tail
        else:
            self.curr = self.curr.prev

    def __iter__(self):
        """
        Makes the DoublyLinkedList iterable
        :return: DoublyLinkedList
        """
        self.curr = None
        return self

    def __next__(self):
        """
        Returns the next item in the list
        :raises: StopIteration if there is no next item
        :return: The next item in the list
        """
        self.next()
        if self.curr is not None:
            return self.curr.value
        else:
            raise StopIteration("List out of bounds: No more values to return")

    def search(self, query: T) -> None:
        """
        Searches the list for a given query and returns the first value in the list that satisfies the query.
        :param query: The query to search for
        :return: The first value in the list that satisfies the query or None if the query is not found
        """
        self._check_type(query)
        if self.is_empty():
            return
        old_current = self.curr

        if self.__last_insert == "front":
            self.curr = self.head
            while self.curr is not None:
                if self.curr.value == query:
                    return
                else:
                    self.next()
            self.curr = old_current
        else:
            self.curr = self.tail
            while self.curr is not None:
                if self.curr.value == query:
                    return
                else:
                    self.previous()
            self.curr = old_current

    def delete(self, value: T, all_occurrences: bool = True) -> None:
        """
        Deletes the value from the list.
        Moves the cursor to before the list
        :param value: The value to be deleted
        :param all_occurrences: True if all the occurrences of the value should be deleted otherwise False
        :return: None
        """
        if self.is_empty():
            raise ContainerEmptyError("Doubly Linked List")

        self.curr = self.head

        while self.curr is not None:
            if self.curr.value == value:
                if self.curr == self.head and not self.is_empty():
                    self.delete_front()
                    if not all_occurrences:
                        self.curr = None
                        return
                if self.curr == self.tail and not self.is_empty():
                    self.delete_back()
                    self.curr = None
                    return

                if self.is_empty():
                    return

                previous = self.curr.prev
                next_ = self.curr.next

                previous.next = next_
                next_.prev = previous
                self.curr = None
                self.curr = self.head
                self.length -= 1
                if not all_occurrences:
                    return

            self.next()
        if not all_occurrences:
            self.curr = None

    def current(self):
        """
        Returns the value of the current node
        :return: The value of the current node
        """
        return self.curr.value if self.curr is not None else None

    def get(self, index: int) -> T | None:
        """
        Gets the value at the given index
        :param index: The index of the value to be returned
        :return: The value at the given index
        """
        self.__prepare_indexing(index)

        old_current = self.curr
        self.curr = self.head

        for i in range(index):
            self.next()

        if self.curr is not None:
            to_return = self.curr.value
            self.curr = old_current
            return to_return

    def __prepare_indexing(self, index: int) -> None:
        """
        Prepares the list for indexing
        :param index: The index to be prepared
        :return: None
        """
        if self.is_empty():
            raise ContainerEmptyError(name="Doubly Linked List")

        if not isinstance(index, int):
            raise TypeError(f"<index> must be of type 'int' not '{type(index)}'")

        if index > (self.length - 1) or index < 0:
            raise IndexError(f"Index '{index}' out of bounds for Doubly Linked List of size '{self.length}'")

    def set(self, index: int, value: T) -> None:
        """
        Sets the value at the given index
        :param index: The index of the value to be set
        :param value: The value to be set
        :return: None
        """
        self.__prepare_indexing(index)

        old_current = self.curr
        self.curr = self.head

        for i in range(index):
            self.next()

        if self.curr is not None:
            self.curr.value = value
            self.curr = old_current

    def len(self) -> int:
        """
        Returns the length of the list
        :return: The length of the list
        """
        return self.length

    def __str__(self) -> str:
        """
        String representation of Doubly Linked List
        :return:
        """
        string = "["
        old_curr = self.curr
        self.curr = self.head

        while self.curr is not None:
            string += f"{self.curr.value}, "
            self.next()

        string = string.rstrip(", ")
        string += "]"

        self.curr = old_curr
        return string

    def foreach(self, fn: Callable[[T], Any] | Callable[[DoublyLinkedNode[T]], Any], node: bool = False) -> Any:
        """
        Executes a function fn on each element of the list
        :param node: True if the foreach should be applied to the node False otherwise
        :param fn: The function to execute
        :return: Any value produced by the function in a list
        """
        if self.is_empty():
            raise IndexError("Cannot get first element of empty list")

        result: list[Any] = []
        old_current = self.curr
        self.curr = self.head
        if node:
            while self.curr is not None:
                result.append(fn(self.curr))
                self.next()
        else:
            while self.curr is not None:
                result.append(fn(self.curr.value))
                self.next()

        self.curr = old_current
        for _ in result:
            if _ is not None:
                return result
        return None

    def contains(self, value: T) -> bool:
        """
        Check if a value is in the List
        :param value: the value to be checked
        :return: True if the value is in the List else False
        """
        if self.is_empty():
            return False

        self._check_type(value)

        old_current = self.curr
        self.search(value)
        _ = True if self.curr is not None and self.curr.value == value else False
        self.curr = old_current
        return _

    def clear(self):
        self.head = None
        self.curr = None
        self.tail = None
        self.length = 0
        self._type = None
