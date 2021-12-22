from ast_.ast_abstract import AtomicNode, UnaryNode, BinaryNode
from automata.automata import Automata
from regex.automata_creation import epsilon_automata, simple_automata, LetterAutomata, NumberAutomata, \
    NumberAndLetterAutomata


class EpsilonNode(AtomicNode):
    
    def __init__(self):
        super().__init__('epsilon')

    def evaluate(self):
        return epsilon_automata()
    

class SymbolNode(AtomicNode):
    
    def evaluate(self):
        return simple_automata(self.token, [])
    

class LetterNode(AtomicNode):
    
    def __init__(self):
        super().__init__('letter')
    
    def evaluate(self):
        return LetterAutomata()
    
    
class NumberNode(AtomicNode):
    
    def __init__(self):
        super().__init__('number')
    
    def evaluate(self):
        return NumberAutomata()
    
    
class NumberAndLetterNode(AtomicNode):
    
    def __init__(self):
        super().__init__('alphanum')
    
    def evaluate(self):
        return NumberAndLetterAutomata()
    
    
class MaybeNode(UnaryNode):
    
    def operate(self, value: Automata):
        return value.union(epsilon_automata())
    
    
class StarNode(UnaryNode):
    
    def operate(self, value: Automata):
        return value.star()


class PlusNode(UnaryNode):
    
    def operate(self, value: Automata):
        return value.concat(value.star())
    
    
class UnionNode(BinaryNode):
    
    def operate(self, left_value: Automata, right_value: Automata):
        return left_value.union(right_value)
    
    
class ConcatNode(BinaryNode):
    
    def operate(self, left_value: Automata, right_value: Automata):
        return left_value.concat(right_value)


