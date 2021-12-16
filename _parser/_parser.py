"""
program -> declaration* EOF;

block -> "{" declaration* "}"

declaration -> varDeclaration | statement
varDeclaration -> "let" IDENTIFIER "=" expression

statement -> expressionStatement

expressionStatement -> expression ";"
expression -> assignment
assignment -> IDENTIFIER "=" equality | equality
equality -> comparison ( ("!=" | "==") comparison)*
comparison -> term ( (">" | ">=" | "<" | "<=") term)*
term ->  factor ( ( "-" | "+" ) factor)*
factor -> unary ( ( "/" | "*" ) unary)*
unary -> ( "!" | "-" ) unary | call
call -> primary ( "("  arguments? ")")?
primary -> NUMBER | STRING | "true" | "false" | "null" | "(" equality ")" | IDENTIFIER
"""

from tokenizer.token_ import Token, TokenType
from .expression import Expression, Assignment, Binary, Unary, Literal, Grouping, Variable
from .statement import ExpressionStatement, VarDeclaration


class Parser:
    def __init__(self, tokens: [Token], scope):
        self.current = 0
        self.tokens = tokens
        self.actual_scope = scope

    def parse(self):
        """
        Parses current Token list, and returns a syntax tree
        """
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self):
        if self.match(TokenType.LET):
            return self.var_declaration()
        return self.statement()

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        self.consume(TokenType.EQUAL, "Variable must be initialized")
        expression = self.expression()
        self.consume(TokenType.SEMICOLON, "; expected")
        return VarDeclaration(name, expression)

    def statement(self):
        return self.expression_statement()

    def expression_statement(self):
        expression = self.expression()
        self.consume(TokenType.SEMICOLON, "; expected")
        return ExpressionStatement(expression)

    def expression(self) -> Expression:
        """
        Solves expression production
        """
        return self.assignment()

    def assignment(self) -> Expression:
        """
        Solves assignment production
        """
        expression = self.equality()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.equality()
            if type(expression) == Variable:
                return Assignment(expression.name, value)
            raise Exception("Invalid assignment")
        return expression

    def variable(self) -> bool:
        """
        Solves variable production
        """
        if self.match(TokenType.LET):  # if the actual token is 'let'
            if self.match(TokenType.IDENTIFIER):  # and the next token is an identifier,
                if self.actual_scope.declaration(self.previous().text):  # then declare the variable
                    return True  # if the variable is declared correctly, return true
                raise Exception()  # else, raise exception
            raise Exception()  # if the next token is not an identifier, raise Exception

        if self.match(TokenType.IDENTIFIER):  # if the actual token is an identifier
            if self.actual_scope.exists_variable(self.previous().text):  # check if it's a valid assignation
                return True  # if it is, return True
            raise Exception()  # else, raise exception

        return False  # otherwise, return False

    def binary(self, expression, *types: [TokenType]) -> Binary:
        """
        Auxiliary method for building binary expressions
        :param expression: expression builder for left and right expressions
        :param types: list of expected TokenTypes for operands
        :return:
        """
        expr = expression()  # builds the expression on the left
        while self.match(*types):
            # while an operator is found, consume the operator and solve the expression on the right
            operator = self.previous()
            right = expression()
            # builds a new binary expression from joining left and right expressions with an operator
            expr = Binary(expr, operator, right)
        # if a binary operator isn't found an expression to parse is returned
        # otherwise the binary expression is returned
        return expr

    def equality(self) -> Expression:
        """
        Solves equality production
        """
        return self.binary(self.comparison, TokenType.EQUAL_EQUAL, TokenType.EQUAL_DIFFERENT)

    def comparison(self) -> Expression:
        """
        Solves comparison production
        """
        return self.binary(self.term, TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LOWER_EQUAL, TokenType.LOWER)

    def term(self) -> Expression:
        """
        Solves term production
        """
        return self.binary(self.factor, TokenType.PLUS, TokenType.MINUS)

    def factor(self) -> Expression:
        """
        Solves factor production
        """
        return self.binary(self.unary, TokenType.MULTIPLY, TokenType.DIVIDE)

    def unary(self) -> Expression:
        """
        Solves unary production
        """
        # checks if current token is an unary operator
        if self.match(TokenType.EXCLAMATION, TokenType.MINUS):
            operator = self.previous()
            # right member is treated as a unary expression to allow nesting (example: !!false)
            right = self.unary()
            return Unary(operator, right)
        # if there's no unary expression check the primary production
        return self.primary()

    def primary(self) -> Expression:
        """
        Solves primary production
        """
        # check if token is false, true, null a string or a number and return a literal with the value
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NULL):
            return Literal(None)
        if self.match(TokenType.NUMBER):
            return Literal(float(self.previous().text))
        if self.match(TokenType.STRING):
            return Literal(self.previous().text)
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LEFT_PARENTHESIS):
            # if it's a left parenthesis, produce the expression and check for right parenthesis
            expr = self.equality()
            self.consume(TokenType.RIGHT_PARENTHESIS, ") missing")
            return Grouping(expr)
        raise Exception()

    def block(self):
        statements = []
        while not self.is_at_end() and not self.check(TokenType.RIGHT_BRACKET):
            statements.append(self.statement())

        self.consume(TokenType.RIGHT_BRACKET, "'}' missing")
        return statements

    def match(self, *types: [TokenType]):
        """
        Checks if current token type is in types
        If the token match is found, the token gets consumed
        """
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def previous(self) -> Token:
        """
        Returns the previous token
        """
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        """
        Consumes a token and returns it
        """
        self.current += 1
        return self.previous()

    def check(self, token_type: TokenType) -> bool:
        """
        Checks if current token is of a certain type
        """
        return not self.is_at_end() and self.peek().type == token_type

    def is_at_end(self) -> bool:
        """
        Returns true if all tokens have been parsed, false otherwise
        """
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        """
        Returns current token
        """
        return self.tokens[self.current]

    def consume(self, token_type: TokenType, message: str):
        if self.check(token_type):
            return self.advance()
        raise Exception(message)
