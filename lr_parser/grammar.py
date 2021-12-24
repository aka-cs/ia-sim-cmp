import itertools as it
from typing import List, Union


class Symbol:
    
    def __init__(self, name: str):
        self.Name = name
    
    def __str__(self):
        return self.Name
    
    def __repr__(self):
        return self.Name
    
    def __add__(self, other: "Symbol"):
        return Sentence(self, other)
    
    def __or__(self, other: Union["Symbol", "Sentence"]):
        if isinstance(other, Symbol) and not isinstance(other, Sentence):
            other = Sentence(other)
        
        return SentenceList(Sentence(self), other)
    
    def __hash__(self):
        return hash(self.Name)
    
    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.Name == other.Name
        return False
    
    @property
    def IsEpsilon(self):
        return False
    
    @property
    def IsTerminal(self):
        return False
    
    @property
    def IsNonTerminal(self):
        return False


class Terminal(Symbol):
    
    @property
    def IsTerminal(self):
        return True


class NonTerminal(Symbol):
    def __init__(self, name):
        super(NonTerminal, self).__init__(name)
        self.productions = []
    
    def __gt__(self, other: Union[Symbol, "Sentence", "SentenceList", tuple]) -> List["Production"]:
        productions = []
        if isinstance(other, Sentence):
            productions = [Production(self, other)]
        
        elif isinstance(other, Symbol):
            productions = [Production(self, Sentence(other))]
        
        elif isinstance(other, SentenceList):
            productions = [Production(self, sentence) for sentence in other.sentences]
            
        elif isinstance(other, tuple):
            if isinstance(other[0], Symbol):
                productions = [AttributedProduction(self, Sentence(other[0]), other[1])]
                
            elif isinstance(other[0], Sentence):
                productions = [AttributedProduction(self, other[0], other[1])]
                
            elif isinstance(other[0], SentenceList):
                productions = [AttributedProduction(self, sentence, other[i + 1])
                               for i, sentence in enumerate(other[0].sentences)]
        
        self.productions += productions
        return productions
    
    def __hash__(self):
        return hash(self.Name)
    
    def __eq__(self, other):
        if isinstance(other, NonTerminal):
            return super(NonTerminal, self).__eq__(other)
        return False
    
    @property
    def IsNonTerminal(self):
        return True


class Sentence:
    
    def __init__(self, *symbols: Symbol):
        self.symbols = symbols
    
    def __add__(self, other: Union[Symbol, "Sentence"]):
        if isinstance(other, Sentence):
            return Sentence(*(self.symbols + other.symbols))
        
        if isinstance(other, Symbol):
            return Sentence(*(self.symbols + (other,)))
    
    def __or__(self, other: Union[Symbol, "Sentence"]):
        if isinstance(other, Sentence):
            return SentenceList(self, other)
        
        if isinstance(other, Symbol):
            return SentenceList(self, Sentence(other))
    
    @property
    def IsEpsilon(self):
        return any(s.IsEpsilon for s in self.symbols)
    
    def __repr__(self):
        return ' '.join(map(repr, self.symbols))
    
    def __len__(self):
        return len(self.symbols)
    
    def __hash__(self):
        return hash(self.symbols)
    
    def __eq__(self, other):
        if not isinstance(other, Sentence):
            return False
        return self.symbols == other.symbols


class Epsilon(Symbol):
    
    def __init__(self):
        super().__init__('epsilon')
        
    def __eq__(self, other):
        return isinstance(other, Epsilon)
    
    def __hash__(self):
        return hash(self.Name)
    
    def __repr__(self):
        return 'e'
    
    @property
    def IsEpsilon(self):
        return True


class EOF(Terminal):
    
    def __init__(self):
        super().__init__('$')


class SentenceList:
    
    def __init__(self, *sentences: Sentence):
        self.sentences = list(sentences)
    
    def __or__(self, other: Sentence | Symbol):
        if isinstance(other, Sentence):
            self.sentences.append(other)
            return self
        
        if isinstance(other, Symbol):
            self.sentences.append(Sentence(other))
            return self


class Production:
    
    def __init__(self, non_terminal: NonTerminal, sentence: Sentence):
        self.Left = non_terminal
        self.Right = sentence
    
    def __iter__(self):
        yield self.Left
        yield self.Right
        
    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return f"{self.Left} -> {self.Right}"
    
    @property
    def IsEpsilon(self):
        return self.Right.IsEpsilon
    
    
class AttributedProduction(Production):
    
    def __init__(self, non_terminal: NonTerminal, sentence: Sentence, attribute):
        super().__init__(non_terminal, sentence)
        self.attribute = attribute


def CreateTerminals(terminals: List[str]) -> List[Terminal]:
    return [Terminal(s) for s in terminals]


def CreateNonTerminals(non_terminals: List[str]) -> List[NonTerminal]:
    return [NonTerminal(s) for s in non_terminals]


class Grammar:
    
    def __init__(self,
                 non_terminals: List[NonTerminal],
                 terminals: List[Terminal],
                 initial: NonTerminal,
                 productions: List[List[Production]]):
        self.NonTerminals = list(non_terminals)
        self.Terminals = list(terminals)
        self.Initial = initial
        self.Epsilon = Epsilon()
        self.EOF = EOF()
        self.Productions: List[Production] = list(it.chain(*productions))
    
    def copy(self):
        g = Grammar(
            list(self.NonTerminals),
            list(self.Terminals),
            self.Initial,
            [list(self.Productions)]
        )
        g.Epsilon = self.Epsilon
        g.EOF = self.EOF
        return g
    
    @property
    def IsAugmentedGrammar(self):
        augmented = 0
        for production in self.Productions:
            if self.Initial == production.Left:
                augmented += 1
        return augmented <= 1

    def AddProductions(self, productions: List[Production], begin=False):
        if not begin:
            for p in productions:
                self.Productions.append(p)
        else:
            self.Productions = productions + self.Productions
    
    def AugmentedGrammar(self, force=False):
        
        if self.IsAugmentedGrammar and not force:
            return self.copy()
        
        g = self.copy()
        
        S = g.Initial
        g.Initial = None
        
        SS = NonTerminal(f"{S}'")
        g.NonTerminals = [SS] + g.NonTerminals
        g.AddProductions(SS > S, True)
        g.Initial = SS
        
        return g


class Item:
    
    def __init__(self, production: Production, pos, lookaheads=None):
        self.production = production
        self.pos = pos
        if lookaheads is None:
            lookaheads = []
        self.lookaheads = frozenset(look for look in lookaheads)

    @property
    def IsReduceItem(self):
        return self.pos == len(self.production.Right)
    
    @property
    def NextSymbol(self) -> Symbol | None:
        if not self.IsReduceItem:
            return self.production.Right.symbols[self.pos]
    
    @property
    def NextItem(self):
        if not self.IsReduceItem:
            return Item(self.production, self.pos + 1, self.lookaheads)
    
    def Preview(self, skip=1):
        unseen = self.production.Right.symbols[self.pos + skip:]
        return [Sentence(*(unseen + (lookahead,))) for lookahead in self.lookaheads]
    
    def Center(self):
        return Item(self.production, self.pos)
        
    def __hash__(self):
        return hash((self.production, self.pos, self.lookaheads))
    
    def __eq__(self, other: "Item"):
        return self.production == other.production and self.pos == other.pos and self.lookaheads == other.lookaheads

    def __repr__(self):
        return f'{self.production.Left} -> {" ".join(map(repr, self.production.Right.symbols[:self.pos]))}.' \
               f'{" ".join(map(repr, self.production.Right.symbols[self.pos:]))},' \
               f' {{{", ".join(map(repr,self.lookaheads))}}}'
