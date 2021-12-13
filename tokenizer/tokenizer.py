from tokenizer.token_type import TokenType
from tokenizer.token_ import Token
from typing import List

import re


class TokenMatcher:
    def __init__(self, regex: str, token_type: TokenType):
        self.regex = re.compile(regex)
        self.token_type = token_type

    def match(self, text):
        m = self.regex.match(text)
        if m:
            text = m.group(0) if not m.groups() else m.group(1)
            return Token(self.token_type, text)
        return None


class Tokenizer:
    def __init__(self, token_matchers: List[TokenMatcher]):
        self.token_matchers = token_matchers

    def cute_analyze(self, program: str) -> [Token]:
        tokens = []
        line = 1
        column = 1
        program = program + '\n'
        while program:
            if program[0] == " ":
                program = program[1:]
                column += 1
                continue
            # current_line = program[:program.find('\n') or len(program)]
            # print(f"matching {current_line}")
            for token_matcher in self.token_matchers:
                token = token_matcher.match(program)
                if token:
                    le = len(token.text)
                    if TokenType.STRING == token_matcher.token_type:
                        le += 2

                    # Saber linea y columna
                    if token_matcher.token_type == TokenType.LINEBREAK:
                        line += 1
                        column = 1
                        program = program[1:]
                        break
                    column += le

                    tokens.append(token)
                    program = program[le:]
                    # print(f"matched with token {token_matcher.token_type}\n")
                    break
            else:
                raise Exception(f'Token could not be matched at line {line}, column {column}')
        tokens.append(Token(TokenType.EOF, ""))
        return tokens

    def old_analyze(self, program: str) -> [Token]:
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

    def analyze(self, program: str) -> [Token]:
        return self.cute_analyze(program)
