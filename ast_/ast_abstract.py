from abc import ABC, abstractmethod


class Node(ABC):
    
    @abstractmethod
    def evaluate(self):
        pass


class AtomicNode(Node, ABC):
    
    def __init__(self, token):
        self.token = token
    
    
class UnaryNode(Node, ABC):
    
    def __init__(self, node: Node):
        self.Node = node

    def evaluate(self):
        value = self.Node.evaluate()
        return self.operate(value)
    
    @abstractmethod
    def operate(self, value):
        pass
    

class BinaryNode(Node, ABC):
    
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right
    
    def evaluate(self):
        left_val = self.left.evaluate()
        right_val = self.right.evaluate()
        return self.operate(left_val, right_val)
        
    @abstractmethod
    def operate(self, left_value, right_value):
        pass
