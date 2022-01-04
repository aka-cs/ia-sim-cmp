import os
import pickle

from tokenizer.token_type import TokenType
from tokenizer.token_ import Token
from automata.automata import Automata
from typing import List

from regex.regex_ import compile_regex
from regex.automata_creation import join_automatas


class TokenMatcher:
    def __init__(self, regex: str, token_type: TokenType):
        self.regex = regex
        self.token_type = token_type
        self._automata = None
        
    @property
    def automata(self):
        if not self._automata:
            self._automata = compile_regex(self.regex)
        return self._automata
    
    @automata.setter
    def automata(self, automata):
        self._automata = automata


class Tokenizer:
    def __init__(self, token_matchers: List[TokenMatcher], path=None):
        loaded = False
        if path:
            try:
                self.automata = pickle.load(open(f'{path}/tokenizer_automata.pkl', 'rb'))
                loaded = True
            except FileNotFoundError:
                pass
        if not loaded:
            self.token_matchers = token_matchers
            for i, token_matcher in enumerate(self.token_matchers):
                token_matcher.automata = token_matcher.automata.add_type((token_matcher.token_type, i))
            self.automata = join_automatas(*map(lambda x: x.automata, token_matchers)).dfa()
            if path:
                os.makedirs(path, exist_ok=True)
                pickle.dump(self.automata, open(f'{path}/tokenizer_automata.pkl', 'wb'))

    def tokenize(self, program: str) -> [Token]:
        return self.automata_tokenize(program)
        
    def automata_tokenize(self, program: str) -> [Token]:
        tokens = []
        line = column = 1
        i = 0
        while i < len(program):
            is_match, length = self.automata.recognize(program, i)
            
            if length == 0:
                raise Exception(f"Unexpected character '{program[i]}' at line: {line} column: {column}")
            
            match = program[i: i + length]
            i += length
            token_type = self.automata.get_type(self.automata.current)
            
            if token_type == TokenType.LINEBREAK:
                line += 1
                column = 0
                continue
                
            if token_type == TokenType.SPACE:
                column += 1
                continue
            
            tokens.append(Token(line, column, token_type, match))
            column += length

        tokens.append(Token(line, column + 1, TokenType.EOF, ""))
        return tokens
            
    
