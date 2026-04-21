class Node:
    def __init__(self,value):
        self.value=value
        self.left=None
        self.right=None
        self.height=1

class avltree:
    def __init__(self):
        self.root=None
    def get_height(self,node):
        if node==None:
            return 0
        else:
            return node.height
    def get_balance(self,node):
        return self.get_height(node.left)-self.get_height(node.right)
    def search(self,node,value):
        if node==None:
            return False
        elif node.value==value:
            return True
        elif node.value<value:
            return self.search(node.right,value)

        elif node.value>value:
            return self.search(node.left,value)
    def right_rotate(self,y):
        x=y.left
        T2 = x.right
        x.right=y
        y.left=T2
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        return x
    def left_rotate(self,y):
        x=y.right
        T2 = x.left
        x.left=y
        y.right=T2
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        return x
    def insert(self,node,value):
        if node==None:
            return Node(value)
        elif value < node.value:
            node.left = self.insert(node.left, value)
        elif value > node.value:
            node.right = self.insert(node.right, value)
        else:
            return node 
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)
        if balance > 1 and value < node.left.value:
            return self.right_rotate(node)
        if balance < -1 and value > node.right.value:
            return self.left_rotate(node)
        if balance > 1 and value > node.left.value:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
        if balance < -1 and value < node.right.value:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)
        return node       
 
    def inorder(self, node):
        res = []
        if node:
            res += self.inorder(node.left)
            res.append(node.value)
            res += self.inorder(node.right)
        return res

    def levelorder(self, root):
        if not root:
            return []
        import collections
        queue = collections.deque([root])
        res = []
        while queue:
            node = queue.popleft()
            res.append(node.value)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return res
    def get_min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def delete(self, node, value):
        if not node:
            return node
        if value < node.value:
            node.left = self.delete(node.left, value)
        elif value > node.value:
            node.right = self.delete(node.right, value)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            temp = self.get_min_value_node(node.right)
            node.value = temp.value
            node.right = self.delete(node.right, temp.value)
        if not node:
            return node
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)
        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.right_rotate(node)
            
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.left_rotate(node)
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)

        return node
    
tree = avltree()
root = None

insert_seq = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45, 55, 65, 75, 85]
for val in insert_seq:
    root = tree.insert(root, val)
    print(f"Insert {val}, Inorder: {tree.inorder(root)}")
    
delete_seq = [20, 60, 30, 80]
for val in delete_seq:
    root = tree.delete(root, val)
    print(f"Delete {val}, Levelorder: {tree.levelorder(root)}")