from lr_parser.lr1_parser import LR1Parser
from lr_parser.grammar import Grammar, CreateTerminals, CreateNonTerminals, Terminal
from lr_parser.lr_utils import evaluate_reverse_parser
from .nodes import *
from tokenizer.token_ import Token, TokenType


class Parser:

    def __init__(self):
        symbol = Terminal("symbol")
        operators = equals, plus, minus, mul, div, exclamation = CreateTerminals("= + - * / !".split())
        comparison = equals_equals, different, greater, greaterequal, less, lessequal = CreateTerminals(
            "== != > >= < <=".split())
        logic = and_operator, or_operator = CreateTerminals("and or".split())
        statements = if_s, else_s, while_s, fun_s, var_s, return_s = CreateTerminals("if else while fun var return".split())
        specials = number, identifier, string = CreateTerminals("number identifier string".split())
        grouping = left_p, right_p, left_b, right_b = CreateTerminals("( ) { }".split())
        punctuation = comma, dot, semicolon = CreateTerminals(", . ;".split())

        terminals = [symbol, *operators, *comparison, *logic, *statements, *specials, *grouping, *punctuation]

        non_terminals \
            = p_statements, p_statement, p_if, p_else, p_while, p_fun_declaration, p_return, p_return_arg,\
            p_params, p_more_params, p_var_declaration, p_assign, p_expression_s, p_expression, p_logic, p_logic_op,\
            p_equality, p_equality_op, p_comparison, p_comparison_op, p_term, p_term_op, \
            p_factor, p_factor_op, p_unary, p_unary_op, p_call, p_arguments, p_more_arguments, p_primary \
            = CreateNonTerminals("Statements Statement If Else While FunDeclaration Return ReturnArg "
                                 "Params MoreParams VarDeclaration Assign ExpressionS Expression Logic Logic_op "
                                 "Equality Equality_op Comparison Comparison_op Term Term_op "
                                 "Factor Factor_op Unary Unary_op Call Arguments MoreArguments Primary".split())

        productions = [
            p_statements > (p_statements + p_statement | p_statement, lambda x: [*x[0], x[1]], lambda x: [x[0]]),
            p_statement > (p_if | p_var_declaration | p_assign | p_fun_declaration | p_return | p_expression_s,
                           lambda x: x[0],
                           lambda x: x[0],
                           lambda x: x[0],
                           lambda x: x[0],
                           lambda x: x[0],
                           lambda x: x[0]),

            p_if > (if_s + left_p + p_expression + right_p + left_b + p_statements + p_else,
                    lambda x: If(x[2], x[5], x[6])),
            p_else > (right_b + else_s + left_b + p_statements + right_b | right_b,
                      lambda x: x[3],
                      lambda x: []),

            p_var_declaration > (var_s + identifier + equals + p_equality + semicolon, lambda x: VarDeclaration(x[1], x[3])),
            p_assign > (identifier + equals + p_equality + semicolon, lambda x: Assignment(x[0], x[2])),
            p_fun_declaration > (fun_s + identifier + left_p + p_params + left_b + p_statements + right_b,
                                 lambda x: Function(x[1], x[3], x[5])),

            p_params > (identifier + p_more_params | right_p, lambda x: [x[0], *x[1]], lambda x: []),
            p_more_params > (comma + identifier + p_more_params | right_p, lambda x: [x[1], *x[2]], lambda x: []),

            p_return > (return_s + p_return_arg, lambda x: Return(x[1])),
            p_return_arg > (p_expression + semicolon | semicolon, lambda x: x[0], lambda x: []),

            p_expression_s > (p_expression + semicolon, lambda x: x[0]),
            p_expression > (p_logic, lambda x: x[0]),
            p_logic > (p_logic + p_logic_op + p_equality | p_equality, lambda x: Binary(*x), lambda x: x[0]),
            p_equality > (p_equality + p_equality_op + p_comparison | p_comparison, lambda x: Binary(*x), lambda x: x[0]),
            p_comparison > (p_comparison + p_comparison_op + p_term | p_term, lambda x: Binary(*x), lambda x: x[0]),
            p_term > (p_term + p_term_op + p_factor | p_factor, lambda x: Binary(*x), lambda x: x[0]),
            p_factor > (p_factor + p_factor_op + p_unary | p_unary, lambda x: Binary(*x), lambda x: x[0]),
            p_unary > (p_unary_op + p_unary | p_call, lambda x: Unary(*x), lambda x: x[0]),
            p_call > (p_primary | p_primary + left_p + p_arguments, lambda x: x[0], lambda x: Call(x[0], x[2])),
            p_primary > (number | string | identifier | left_p + p_logic + right_p,
                         lambda x: Literal(float(x[0].text)),
                         lambda x: Literal(x[0].text),
                         lambda x: Variable(x[0]),
                         lambda x: x[1]),

            p_arguments > (p_expression + p_more_arguments | right_p, lambda x: [x[0], *x[1]], lambda x: []),
            p_more_arguments > (comma + p_expression + p_more_arguments | right_p, lambda x: [x[1], *x[2]], lambda x: []),

            p_logic_op > (and_operator | or_operator, lambda x: x[0], lambda x: x[0]),
            p_equality_op > (equals_equals | different, lambda x: x[0], lambda x: x[0]),
            p_comparison_op > (greater | greaterequal | less | lessequal,
                               lambda x: x[0], lambda x: x[0], lambda x: x[0], lambda x: x[0]),
            p_term_op > (plus | minus, lambda x: x[0], lambda x: x[0]),
            p_factor_op > (mul | div, lambda x: x[0], lambda x: x[0]),
            p_unary_op > (exclamation | minus, lambda x: x[0], lambda x: x[0])
        ]

        grammar = Grammar(non_terminals, terminals, p_statements, productions)

        self.parser = LR1Parser(grammar)
        self.mapping = {
            TokenType.IDENTIFIER: identifier,
            TokenType.NUMBER: number,
            TokenType.STRING: string,
            TokenType.EQUAL: equals,
            TokenType.EQUAL_EQUAL: equals_equals,
            TokenType.EQUAL_DIFFERENT: different,
            TokenType.GREATER: greater,
            TokenType.GREATER_EQUAL: greaterequal,
            TokenType.LESS: less,
            TokenType.LESS_EQUAL: lessequal,
            TokenType.IF: if_s,
            TokenType.ELSE: else_s,
            TokenType.WHILE: while_s,
            TokenType.FUN: fun_s,
            TokenType.RETURN: return_s,
            TokenType.VAR: var_s,
            TokenType.LEFT_PARENTHESIS: left_p,
            TokenType.RIGHT_PARENTHESIS: right_p,
            TokenType.LEFT_BRACKET: left_b,
            TokenType.RIGHT_BRACKET: right_b,
            TokenType.AND: and_operator,
            TokenType.OR: or_operator,
            TokenType.PLUS: plus,
            TokenType.MINUS: minus,
            TokenType.MULTIPLY: mul,
            TokenType.DIVIDE: div,
            TokenType.EXCLAMATION: exclamation,
            TokenType.COMMA: comma,
            TokenType.DOT: dot,
            TokenType.SEMICOLON: semicolon,
            TokenType.EOF: self.parser.G.EOF
        }

    def _map_tokens_to_terminals(self, tokens: [Token]):
        mapped_tokens = []
        for token in tokens:
            mapped_tokens.append(self.mapping.get(token.type, self.parser.G.Terminals[0]))
        return mapped_tokens

    def parse(self, tokens: [Token]):
        mapped_tokens = self._map_tokens_to_terminals(tokens)
        parsed, operations = self.parser(mapped_tokens)
        ast = evaluate_reverse_parser(parsed, operations, tokens + [self.parser.G.EOF])
        return ast
