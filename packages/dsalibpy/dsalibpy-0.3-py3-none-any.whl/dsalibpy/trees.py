class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if not self.root:
            self.root = TreeNode(value)
        else:
            self._insert(self.root, value)

    def _insert(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
            else:
                self._insert(node.left, value)
        else:
            if node.right is None:
                node.right = TreeNode(value)
            else:
                self._insert(node.right, value)

    def in_order_traversal(self, node):
        return (self.in_order_traversal(node.left) if node.left else []) + [node.value] + (self.in_order_traversal(node.right) if node.right else [])

class BinarySearchTree(BinaryTree):
    pass

class AVLTree(BinarySearchTree):
    # Implement AVL Tree specifics here
    pass

class RedBlackTree(BinarySearchTree):
    # Implement Red-Black Tree specifics here
    pass
