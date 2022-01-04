import os
import pickle
from abc import abstractmethod
from enum import Enum, auto

from lr_parser.grammar import Grammar


class Action(Enum):
    SHIFT = auto()
    REDUCE = auto()
    OK = auto()


class ShiftReduceParser:
    
    def __init__(self, g: Grammar, logs=False, path=None):
        self.G = g
        self.logs = logs
        self.action = {}
        self.goto = {}
        self.index_action = {}
        self.index_goto = {}
        loaded = False
        if path:
            try:
                if open(f'{path}/parser_grammar.hash', 'r').read() == self.G.to_string():
                    self.pickle_load(path)
                    loaded = True
            except FileNotFoundError:
                pass
        if not loaded:
            self._build_parsing_table()
            # pickle save
            if path:
                self.pickle_save(path)
        
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

    def pickle_save(self, path):
        os.makedirs(path, exist_ok=True)
        
        # Action table
        self.index_action = {}
        for k, (action, v) in self.action.items():
            if action != Action.REDUCE:
                self.index_action[k] = (action, v)
                continue
            self.index_action[k] = (action, self.G.Productions.index(v))
        pickle.dump(self.index_action, open(f'{path}/parser_index_action.pkl', 'wb'))
        
        # GoTo table
        self.index_goto = {}
        for (i, non_terminal), v in self.goto.items():
            self.index_goto[i, self.G.NonTerminals.index(non_terminal)] = v
        pickle.dump(self.index_goto, open(f'{path}/parser_index_goto.pkl', 'wb'))
        
        with open(f'{path}/parser_grammar.hash', 'w') as f:
            f.write(self.G.to_string())

    def pickle_load(self, path):
        # Action table
        self.index_action = pickle.load(open(f'{path}/parser_index_action.pkl', 'rb'))
        for k, (action, v) in self.index_action.items():
            if action != Action.REDUCE:
                self.action[k] = (action, v)
                continue
            self.action[k] = (action, self.G.Productions[v])
            
        # GoTo table
        self.index_goto = pickle.load(open(f'{path}/parser_index_goto.pkl', 'rb'))
        for (i, index), v in self.index_goto.items():
            self.goto[i, self.G.NonTerminals[index]] = v
                    
