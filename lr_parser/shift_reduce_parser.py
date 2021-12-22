from abc import abstractmethod
from enum import Enum, auto

from lr_parser.grammar import Grammar


class Action(Enum):
    SHIFT = auto()
    REDUCE = auto()
    OK = auto()


class ShiftReduceParser:
    
    def __init__(self, g: Grammar, logs=False):
        self.G = g
        self.logs = logs
        self.action = {}
        self.goto = {}
        self._build_parsing_table()
        
    @abstractmethod
    def _build_parsing_table(self):
        pass
    
    def __call__(self, w):
        stack = [0]
        cursor = 0
        output = []
        operations = []
        
        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.logs:
                print(stack, w[cursor:])

            try:
                action, tag = self.action[state, lookahead]
            except KeyError as k:
                raise Exception(k)
            
            if self.logs:
                print(action, tag)
                
            match action:
                case Action.SHIFT:
                    operations.append(action)
                    stack.append(lookahead)
                    stack.append(tag)
                    cursor += 1
                case Action.REDUCE:
                    operations.append(action)
                    for symbol in reversed(tag.Right.symbols):
                        stack.pop()
                        assert stack.pop() == symbol
                    output.append(tag)
                    goto = self.goto[stack[-1], tag.Left]
                    stack.append(tag.Left)
                    stack.append(goto)
                case Action.OK:
                    stack.pop()
                    assert stack.pop() == self.G.Initial
                    assert len(stack) == 1 and stack[-1] == 0
                    return output, operations
                case _:
                    raise Exception()
                    
