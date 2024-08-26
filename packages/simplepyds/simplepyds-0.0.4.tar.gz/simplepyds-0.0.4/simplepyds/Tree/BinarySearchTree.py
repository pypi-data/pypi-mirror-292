from typing import Callable, Literal, Any
from simplepyds.Base.Container import Container
from simplepyds.Tree.TreeNode import BinarySearchTreeNode


class BinarySearchTree[T](Container):
    def __init__(self, comparator: Callable[[T, T], bool] | None = None):
        """
        :param comparator: Callable[[T, T], bool] | None: A function that takes two T and returns True if the first T
        is greater than the second.
        """
        super().__init__()
        self._head: BinarySearchTreeNode[T] | None = None
        self._size: int = 0
        self._comparator = comparator
        self._type = None

    def insert(self, value: T) -> None:
        """
        Inserts the given value into the tree
        :param value: The value to insert
        :return: None
        """
        self._check_type(value)

        if self.is_empty():
            self._head = BinarySearchTreeNode(value)
            self._size += 1
            return

        self._head = self._insert(self._head, value)
        self._size += 1

    def _insert(self, root: BinarySearchTreeNode[T] | None, value: T) -> BinarySearchTreeNode[T]:
        """
        Inserts the given value into the tree
        :param root: The root of the tree
        :param value: The value to insert
        :return: The tree resulting from the insertion
        """
        if root is None:
            return BinarySearchTreeNode(value)

        if isinstance(value, (int, float, str)):
            if root is not None:
                if root.value >= value:
                    root.left = self._insert(root.left, value)
                if root.value < value:
                    root.right = self._insert(root.right, value)
        else:
            if self._comparator:
                if root is not None:
                    if self._comparator(root.value, value):
                        root.left = self._insert(root.left, value)
                    if self._comparator(value, root.value):
                        root.right = self._insert(root.right, value)
            else:
                raise NotImplementedError(f"Cannot compare <{type(self._type)}> without a comparator.\n"
                                          f"Please set a comparator.")

        return root

    def traverse(self, mode: Literal["in-order", "pre-order", "post-order"] = "in-order") -> None:
        """
        Traverses the tree
        :param mode: traversal mode used to traverse the tree
        :return: None
        """
        self._traverse(self._head, mode)

    def _traverse(
            self, root: BinarySearchTreeNode[T] | None,
            mode: Literal["in-order", "pre-order", "post-order"] = "in-order",
            visit: Callable[[T], Any] | None = None
    ):
        """
        Traverses the tree
        :param root: The root of the tree
        :param mode: The traversal mode used to traverse the tree
        :param visit: A function that takes a T as an argument and does something with it.
        :return: None
        """
        if root is not None:
            if mode == "pre-order":
                if visit is not None:
                    visit(root.value)
                self._traverse(root.left, mode, visit)
                self._traverse(root.right, mode, visit)

            if mode == "in-order":
                self._traverse(root.left, mode, visit)
                if visit is not None:
                    visit(root.value)
                self._traverse(root.right, mode, visit)

            if mode == "post-order":
                self._traverse(root.left, mode, visit)
                self._traverse(root.right, mode, visit)
                if visit is not None:
                    visit(root.value)

    def head(self) -> T:
        """
        Returns the value of the head of the tree
        :return: The value of the head of the tree
        """
        if self._head is not None:
            return self._head.value

    def is_empty(self) -> bool:
        """
        Checks if the tree is empty
        :return: True if the tree is empty, False otherwise
        """
        return True if self._head is None else False

    def size(self) -> int:
        """
        Returns the size of the tree
        :return: the size of the tree
        """
        return self._size

    def foreach(self, visit_fn: Callable[[T], Any]) -> None:
        """
        Traverses the tree and calls visit_fn for each element in the tree
        :param visit_fn: The function that takes a T as an argument and does something with it.
        :return: None
        """
        if not self.is_empty():
            self._traverse(self._head, mode="in-order", visit=visit_fn)

    def min(self) -> T:
        """
        Returns the value of the minimum element in the tree
        :return: the value of the minimum element in the tree
        """
        if not self.is_empty():
            return self._min(self._head)
        else:
            raise IndexError("Cannot get minimum of empty Binary Search Tree")

    def _min(self, root: BinarySearchTreeNode[T]) -> T:
        """
        Returns the value of the minimum element in the tree
        :param root: the root of the tree
        :return: The value of the minimum element in the tree
        """
        if root is not None:
            if root.left is not None:
                return self._min(root.left)
            else:
                return root.value
        else:
            raise RuntimeError("A <None> root was passed to the _min() function.")

    def max(self) -> T:
        """
        Returns the value of the maximum element in the tree
        :return: The value of the maximum element in the tree
        """
        if not self.is_empty():
            return self._max(self._head)
        else:
            raise IndexError("Cannot get maximum of empty Binary Search Tree")

    def _max(self, root: BinarySearchTreeNode[T]) -> T:
        """
        Returns the value of the maximum element in the tree
        :param root: The root of the tree
        :return: Returns the value of the maximum element in the tree
        """
        if root is not None:
            if root.right is not None:
                return self._max(root.right)
            else:
                return root.value
        else:
            raise RuntimeError("A <None> root was passed to the _max() function")

    def __str__(self):
        """
        Returns a string representation of the tree
        :return: a string representation of the tree
        """
        if self._head is not None:
            return (f"Head: {self._head}\n"
                    f"\tleft: {self._head.left}\n"
                    f"\tright: {self._head.right}")
        else:
            return str(None)

    def search(self, value: T) -> bool:
        """
        Looks for a value in the tree
        :param value: The value to search
        :return: True if the value was found, False otherwise
        """
        if not self.is_empty():
            self._check_type(value)
            return self._search(self._head, value)
        else:
            raise IndexError(f"Cannot search for value <{value}> in empty Binary Search Tree")

    def _search(self, root: BinarySearchTreeNode[T], value: T) -> bool:
        """
        Looks for a value in the tree
        :param root: The root of the tree
        :param value: The value to search
        :return: True if the value was found, False otherwise
        """
        if isinstance(value, (int, float, str)):
            if root is not None:
                if root.value == value:
                    return True
                elif root.value >= value:
                    if root.left is not None:
                        return self._search(root.left, value)
                    else:
                        return False
                if root.value < value:
                    if root.right is not None:
                        return self._search(root.right, value)
                    else:
                        return False
            else:
                raise RuntimeError("Root of <None> was passed to _search function")

        else:
            if self._comparator is not None:
                if root is not None:
                    if root.value == value:
                        return True
                    if self._comparator(root.value, value):
                        if root.left is not None:
                            return self._search(root.left, value)
                        else:
                            return False
                    if self._comparator(value, root.value):
                        if root.right is not None:
                            return self._search(root.right, value)
                        else:
                            return False
                else:
                    raise RuntimeError("Root of <None> was passed to _search()")
            else:
                raise TypeError(f"Cannot compare {type(value)} without a comparator function.")

    def delete(self, value: T) -> None:
        """
        Removes a value from the tree
        :param value: the value to remove
        :return: None
        """
        self._check_type(value)
        if not self.is_empty():
            if self.search(value):
                self._head = self._delete(value, self._head)
                self._size -= 1
            else:
                return None
        else:
            raise IndexError("Cannot delete from empty Binary Search Tree")

    def _delete(self, value: T, root: BinarySearchTreeNode[T]) -> BinarySearchTreeNode[T] | None:
        """
        Removes a value from the tree
        :param value: The value to remove
        :param root: The root of the tree
        :return: A BinarySearchTreeNode[T] that is the result of deleting the value from the tree
        """
        if root is None:
            return None

        if isinstance(value, (int, float, str)):
            if value < root.value:
                root.left = self._delete(value, root.left)
            elif value > root.value:
                root.right = self._delete(value, root.right)
            else:
                # We have found the rood that we want to delete
                if root.left is None:
                    return root.right
                if root.right is None:
                    return root.left

                # in order successor (smallest of the right subtree)
                in_order_successor = self._min(root.right)
                root.value = in_order_successor
                root.right = self._delete(value, root.right)

        else:
            if self._comparator:
                if self._comparator(root.value, value):
                    root.left = self._delete(value, root.left)
                elif self._comparator(value, root.value):
                    root.right = self._delete(value, root.right)
                else:
                    # We have found the rood that we want to delete
                    if root.left is None:
                        return root.right
                    if root.right is None:
                        return root.left

                    # in order successor (smallest of the right subtree)
                    in_order_successor = self._min(root.right)
                    root.value = in_order_successor
                    root.right = self._delete(value, root.right)
            else:
                raise NotImplementedError(f"Cannot compare <{type(self._type)}> without a comparator.\n"
                                        f"Please set a comparator.")

        return root
