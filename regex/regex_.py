from typing import List

from lr_parser.lr1_parser import LR1Parser
from lr_parser.grammar import Grammar, NonTerminal, Terminal, CreateTerminals, CreateNonTerminals, Epsilon
from lr_parser.lr_utils import evaluate_reverse_parser
from tools.decorators import only_once
from regex.regex_ast import ConcatNode, UnionNode, StarNode, SymbolNode, MaybeNode, NumberNode, \
    NumberAndLetterNode, LetterNode, PlusNode, RangeNode, SymbolInBracketsNode, ConcatInBracketsNode, BracketNode, \
    BracketComplimentNode


@only_once
def RegParser():
    terminals = symbol, pipe, star, o_par, c_par, maybe, number, letter, alphanum, plus,\
        o_bracket, c_bracket, minus, compliment =\
        CreateTerminals(r'symbol | * ( ) ? \d \l \w + [ ] - ^'.split())
    E: NonTerminal
    non_terminals = E, A, S, B, G, F, V, K = CreateNonTerminals('E A S B G F V K'.split())
    
    RegGrammar = Grammar(non_terminals, terminals, E, [
        E > (E + pipe + A | A,
             lambda x: UnionNode(x[0], x[2]), lambda x: x[0]),
        A > (A + S | S,
             lambda x: ConcatNode(x[0], x[1]), lambda x: x[0]),
        S > (B + star | B + plus | B + maybe | B,
             lambda x: StarNode(x[0]), lambda x: PlusNode(x[0]),
             lambda x: MaybeNode(x[0]), lambda x: x[0]),
        B > (symbol | o_par + E + c_par | o_bracket + G + c_bracket | number | letter | alphanum,
             lambda x: SymbolNode(x[0]), lambda x: x[1], lambda x: x[1], lambda x: NumberNode(),
             lambda x: LetterNode(), lambda x: NumberAndLetterNode()),
        G > (compliment + F | F,
             lambda x: BracketComplimentNode(x[1]), lambda x: BracketNode(x[0])),
        F > (F + V | V,
             lambda x: ConcatInBracketsNode(x[0], x[1]), lambda x: x[0]),
        V > (V + minus + K | K,
             lambda x: RangeNode(x[0], x[2]), lambda x: x[0]),
        K > (symbol,
             lambda x: SymbolInBracketsNode(x[0]))
    ])
    
    return LR1Parser(RegGrammar)


def _tokenize(regex: str):
    tokens = []
    backslash = ''
    for x in regex:
        if x == '\\' and backslash == '':
            backslash = '\\'
            continue
        x = backslash + x
        backslash = ''
        tokens.append(x)
    return tokens


def _map_to_regex(tokens: List[str], non_terminals: List[Terminal], default: Terminal):
    mapped_tokens = []
    brackets = False
    for x in tokens:
        matched = False
        for non_terminal in non_terminals:
            if not brackets and x not in '^-' and non_terminal.Name == x:
                matched = True
                mapped_tokens.append(non_terminal)
                if x == '[':
                    brackets = True
            elif brackets and x in '^-]' and non_terminal.Name == x:
                matched = True
                mapped_tokens.append(non_terminal)
                if x == ']':
                    brackets = False
        if not matched:
            mapped_tokens.append(default)
    return mapped_tokens


def _unescape_tokens(tokens: List[str], mapped: List[Terminal], symbol: Terminal):
    tokens_ = []
    for i in range(len(tokens)):
        if mapped[i] == symbol and tokens[i].startswith('\\'):
            tokens_.append(tokens[i][1:])
        else:
            tokens_.append(tokens[i])
    return tokens_


def compile_regex(regex: str):
    parser = RegParser()
    
    tokens = _tokenize(regex)
    
    mapped_tokens = _map_to_regex(tokens, parser.G.Terminals, parser.G.Terminals[0])
    
    mapped_tokens.append(parser.G.EOF)
    
    parsed, operations = parser(mapped_tokens)
    
    real_tokens = _unescape_tokens(tokens, mapped_tokens, parser.G.Terminals[0])
    
    ast = evaluate_reverse_parser(parsed, operations, real_tokens + [parser.G.EOF])
    
    automata = ast.evaluate()
    
    return automata.dfa()
