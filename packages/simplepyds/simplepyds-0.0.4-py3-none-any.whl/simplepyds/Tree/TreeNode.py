from typing import List


class BinarySearchTreeNode[T]:

    def __init__(self, value: T, left: "BinarySearchTreeNode[T] | None" = None, right: "BinarySearchTreeNode[T] | None" = None):
        self.left = left
        self.right = right
        self.value = value

    def __str__(self) -> str:
        return str(self.value)
