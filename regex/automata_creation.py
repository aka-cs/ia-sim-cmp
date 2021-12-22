import string

from automata.automata import Automata
from tools.decorators import only_once


@only_once
def epsilon_automata() -> Automata:
    return Automata(1, {}, {0: []})


def simple_automata(char: str, tags) -> Automata:
    return Automata(2, {(0, char): (1,)}, {1: tags})


def join_automatas(*automatas: Automata) -> Automata:
    if len(automatas) == 1:
        return automatas[0]
    return automatas[0].union(join_automatas(*automatas[1:]))


@only_once
def LetterAutomata() -> Automata:
    return join_automatas(*[simple_automata(char, []) for char in string.ascii_letters])


@only_once
def NumberAutomata() -> Automata:
    return join_automatas(*[simple_automata(char, []) for char in string.digits])


@only_once
def NumberAndLetterAutomata() -> Automata:
    return LetterAutomata().union(NumberAutomata())
