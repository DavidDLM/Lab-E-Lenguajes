from queue import LifoQueue  # For stack operations
import re
import graphviz as gv


# Machine class
class Machine:
    def __init__(this, startingState, finalState):
        this.transitions = []
        this.startingState = startingState
        this.finalState = finalState
        this.states = []

    def getFinalMachineState(this):
        return this.finalState

    def getInitialMachineState(this):
        return this.startingState

    def getStates(this):
        states = []
        for transition in this.transitions:
            if transition.state not in states:
                states.append(transition.state)
            if transition.next not in states:
                states.append(transition.next)
        this.states = sorted(states)

    def display(this):
        states = []
        for transition in this.transitions:
            if transition.state not in states:
                states.append(transition.state)
            if transition.next not in states:
                states.append(transition.next)


# State class
class State:
    def __init__(this, state_id):
        this.state_id = state_id

    def __repr__(this):
        return str(this.state_id)


# Transitions class
class Transition:
    def __init__(this, state, symbol, next):
        this.state = state
        this.next = next
        this.symbol = symbol


# Clase Node based in a node from Linked List
# https://www.tutorialspoint.com/python_data_structure/python_linked_lists.htm
class Node(object):
    # Node class with parents, right node, left node, symbols
    def __init__(this, symbol, parent, prev, next):
        this.symbol = symbol
        this.parent = parent
        this.prev = prev
        this.next = next
        this.nullable = False
        this.firstpos = []
        this.lastpos = []
        this.followpos = []
        this.pos = None


# Stack class with stack functions
# Import LastInFirstOut
# https://codefather.tech/blog/create-stack-python/#:~:text=To%20create%20a%20stack%20in%20Python%20you%20can%20use%20a,the%20top%20of%20the%20stack.
class Stack:
    def __init__(this):
        this.stack = []

    def is_empty(this):
        return not this.stack

    def peek(this):
        return this.stack[-1] if not this.is_empty() else "$"

    def pop(this):
        return this.stack.pop() if not this.is_empty() else "$"

    def push(this, op):
        this.stack.append(op)


# Set class
class Set:
    def __init__(this):
        this.heart = {}
        this.productions = {}
        this.rest = {}
        this.state = 0

    def getHeart(this):
        return this.heart

    def getRest(this):
        return this.rest

    def getProductions(this):
        return this.productions


# Tokens class
class Tokens():
    def __init__(this):
        this.tokens = []

    # Regex defined as bucle
    def tokenize(this, file):
        with open(file, 'r') as f:
            archiveLines = f.read()
        variables = re.findall(r'\s*(\w+)\s*{', archiveLines)
        tokenStrip = r'let\s+([a-zA-Z0-9_-]+)\s+=\s+(.*)'
        for line in archiveLines.splitlines():
            match = re.match(tokenStrip, line.strip())
            if match and match.group(1) in variables:
                this.tokens.append((match.group(1), match.group(2)))
        return this.tokens


# LRParser class
'''
grammar = {
    'S': ['A B', 'C'],
    'A': ['a A', 'b'],
    'B': ['c'],
    'C': ['d', '']
}

S -> A B | C
A -> a A | b
B -> c
C -> d | ε

parser = Parser(grammar, symbols)

first = parser.first(symbol)
result = result.union(parser.goto(no_terminal))
closure = parser.closure(items)

'''


# Grammar class
class Grammar:
    def __init__(this):
        this.initialState = None
        this.terminals = []
        this.nonTerminals = []
        this.first = {}
        this.follow = {}
        this.productions = {}

    def getTerminals(this):
        return this.terminals

    def getNonTerminals(this):
        return this.nonTerminals

    def getInitialState(this):
        return this.initialState

    def getProductions(this):
        return this.productions


# Parser class
class LR0Automaton:
    def __init__(this, grammar, symbols):
        this.grammar = grammar
        this.symbols = symbols

    def first(this, simbolo):
        if simbolo in this.grammar:
            productions = this.grammar[simbolo]
            result = set()
            for production in productions:
                first = this.first(production[0])
                result = result.union(first)
            return result
        else:
            return {simbolo}

    def goto(this, no_terminal):
        result = set()
        if no_terminal == 'S':
            result.add('$')
        for simbolo in this.grammar:
            productions = this.grammar[simbolo]
            for production in productions:
                symbols = production.split()
                if no_terminal in symbols:
                    idx = symbols.index(no_terminal)
                    if idx < len(symbols)-1:
                        first = this.first(symbols[idx+1])
                        result = result.union(first)
                    else:
                        if simbolo != no_terminal:
                            result = result.union(this.goto(simbolo))
        return result

    def closure(this, items):
        closure = items
        new_items = True
        while new_items:
            new_items = False
            for item in closure.copy():
                parts = item.split(' -> ')
                if parts[1] != '':
                    symbols = parts[1].split()
                    if symbols[0] in this.grammar:
                        firsts = this.first(symbols[1])
                        for production in this.grammar[symbols[0]]:
                            new_item = symbols[0] + ' -> . ' + production
                            if new_item not in closure:
                                new_items = True
                                closure.add(new_item)
                                closure = closure.union(
                                    this.closure({new_item}))
                        if 'ε' in firsts:
                            new_item = parts[0] + \
                                ' -> ' + ' '.join(symbols[1:])
                            if new_item not in closure:
                                new_items = True
                                closure.add(new_item)
                                closure = closure.union(
                                    this.closure({new_item}))
        return closure
