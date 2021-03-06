from tokenizer.token_type import TokenType


class Token:

    def __init__(self, line: int, column: int, token_type: TokenType, text: str):
        self.line: int = line
        self.column: int = column
        self.type: TokenType = token_type
        self.text: str = text

    def __str__(self):
        return f"{self.__class__}(type: {self.type}, text: \"{self.text}\")"

    def __repr__(self):
        return self.__str__()
