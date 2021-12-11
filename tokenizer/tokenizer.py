from tokenizer.token_type import TokenType
from tokenizer.token_ import Token
from typing import List

import re


class TokenMatcher:
    def __init__(self, regex: str, token_type: TokenType):
        self.regex = re.compile(regex)
        self.token_type = token_type

    def match(self, text):
        if self.regex.match(text):
            return Token(self.token_type, text)
        return None


class Tokenizer:
    def __init__(self, token_matchers: List[TokenMatcher]):
        self.token_matchers = token_matchers

    def analyze(self, program: str) -> [Token]:
        string_list = program.split('"')
        word_list = []
        for i in range(len(string_list)):
            if i % 2 == 0:
                word_list.extend(string_list[i].split())
            else:
                word_list.append(f'"{string_list[i]}"')
        tokens = []
        for word in word_list:
            for token_matcher in self.token_matchers:
                token = token_matcher.match(word)
                if token:
                    tokens.append(token)
                    break
        tokens.append(Token(TokenType.EOF, ""))
        return tokens
