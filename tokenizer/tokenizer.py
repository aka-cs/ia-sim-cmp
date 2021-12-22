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
        self.automata: Automata = compile_regex(regex)


class Tokenizer:
    def __init__(self, token_matchers: List[TokenMatcher]):
        self.token_matchers = token_matchers
        for i, token_matcher in enumerate(self.token_matchers):
            token_matcher.automata = token_matcher.automata.add_type((token_matcher.token_type, i))
        self.automata = join_automatas(*map(lambda x: x.automata, token_matchers)).dfa()

    def tokenize(self, program: str) -> [Token]:
        return self.automata_tokenize(program)
        
    def automata_tokenize(self, program: str) -> [Token]:
        tokens = []
        line = column = 0
        i = 0
        while i < len(program):
            is_match, length = self.automata.recognize(program, i)
            
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
            
    
