import string
from typing import List

from ast_.ast_abstract import AtomicNode, UnaryNode, BinaryNode
from automata.automata import Automata
from regex.automata_creation import epsilon_automata, simple_automata, LetterAutomata, NumberAutomata, \
    NumberAndLetterAutomata, join_automatas


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


class BracketNode(UnaryNode):
    
    def operate(self, value):
        if not isinstance(value, list):
            value = [value]
        return join_automatas(*[simple_automata(chr(x), []) for x in value])


class BracketComplimentNode(UnaryNode):
    
    def operate(self, value):
        if not isinstance(value, list):
            value = [value]
        value = list(map(chr, value))
        value = [x for x in string.printable if x not in value]
        return join_automatas(*[simple_automata(x, []) for x in value])
        

class SymbolInBracketsNode(AtomicNode):
    
    def evaluate(self):
        return ord(self.token)


class ConcatInBracketsNode(BinaryNode):
    
    def operate(self, left_value, right_value):
        if not isinstance(left_value, list):
            left_value = [left_value]
        if not isinstance(right_value, list):
            right_value = [right_value]
        return left_value + right_value


class RangeNode(BinaryNode):
    
    def operate(self, left_value: chr, right_value: chr):
        return [x for x in range(left_value, right_value + 1)]
