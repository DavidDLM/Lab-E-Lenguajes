# Parser.py
import copy
import pydot
from machine import *
from collections import OrderedDict


class Parser:
    def __init__(this, filename, output=None):
        try:
            this.output = output
            this.errors = False
            this.stateCount = 0
            this.result = None
            this.filename = filename
            this.file = open(filename, 'r')
            this.lines = this.file.readlines()
        except FileNotFoundError:
            raise Exception('File could not be opened')

    def compiler(this):
        this.detect_and_handle_errors()
        this.process_tokens()
        this.build_and_transform_grammar()

    def detect_and_handle_errors(this):
        errors = []
        def add_error(message):
            errors.append(message)
        def is_valid_comment(line):
            return line.startswith("/*") and not line.endswith("*/")
        def is_valid_token(line):
            return line.startswith("%") and line != '%%'
        def is_valid_token_declaration(line):
            return line.startswith("%token")
        def is_valid_ignore(line):
            return line.startswith("IGNORE")
        def is_missing_mark(line):
            return line == '%%'
        exist = False
        for i, line in enumerate(this.lines):
            line = line.strip()

            if is_valid_comment(line):
                add_error("Invalid comment format")

            if line.endswith("*/") and not line.startswith("/*"):
                add_error("Invalid comment format")

            if is_valid_token(line):
                if exist:
                    add_error("Invalid token")
                if is_valid_token_declaration(line):
                    words = line.split()
                    if len(words) < 2:
                        add_error("Unidentified %token")
                else:
                    add_error("Invalid 'token' format")
            if 'token' in line and not line.startswith("%"):
                add_error("Invalid '%token' format")
            if is_valid_ignore(line):
                words = line.split()
                if len(words) < 2:
                    add_error("Unidentified 'IGNORE'")
            if is_missing_mark(line):
                exist = True
        if not exist:
            add_error("Missing '%%' mark")
        if errors:
            error_message = "\n".join(set(errors))
            raise Exception(error_message)
        return None

    def process_tokens(this):
        tokens = set()
        ignored_tokens = set()
        all_tokens_present = True
        with open('Productions/tokens.txt', 'r') as file:
            file_tokens = {line.strip() for line in file}
        for line in this.lines:
            line = line.strip()
            if line == '%%':
                break
            if line.startswith('/*') and line.endswith('*/'):
                continue
            if line.startswith('%token'):
                line_tokens = line.split()[1:]
                tokens.update(line_tokens)
            if line.startswith('IGNORE'):
                ignored_tokens.update(line.split()[1:])
        tokens = list(tokens - ignored_tokens)
        for token in tokens:
            if token not in file_tokens:
                print(f"{token}: Not detected")
                all_tokens_present = False
        return all_tokens_present, tokens

    def build_and_transform_grammar(this):
        grammar = Grammar()
        nonTerminals = set()
        terminals = set()
        productions_found = False
        nonterm = None
        prods = []
        tempGrammar = None
        newInitialState = None

        for line in this.lines:
            line = line.strip()
            if not productions_found:
                if line == '%%':
                    productions_found = True
                continue
            if line.endswith(":"):
                if nonterm is not None:
                    grammar.productions[nonterm] = prods
                    nonTerminals.add(nonterm)
                nonterm = line[:-1].strip()
                prods = []
            elif line and not line.startswith('/*') and line != ';':
                productions = [prod.strip()
                               for prod in line.split("|") if prod.strip()]
                prods.extend(productions)
                for prod in productions:
                    for symbol in prod.split():
                        if symbol.islower():
                            nonTerminals.add(symbol)
                        elif symbol != ";":
                            terminals.add(symbol)
        if nonterm is not None:
            grammar.productions[nonterm] = prods
            nonTerminals.add(nonterm)
        grammar.productions = {nonterm: [prod for prod in prods if prod != ";"]
                               for nonterm, prods in grammar.productions.items()}
        grammar.initialState = next(iter(grammar.productions.keys()))
        grammar.nonTerminals = sorted(nonTerminals)
        grammar.terminals = sorted(terminals)
        tempGrammar = copy.deepcopy(grammar)
        newInitialState = tempGrammar.initialState + "'"
        if newInitialState in tempGrammar.productions:
            tempGrammar.productions[newInitialState].insert(
                0, tempGrammar.initialState)
            tempGrammar.productions.move_to_end(newInitialState, last=False)
        else:
            tempGrammar.productions = OrderedDict(
                [(newInitialState, [tempGrammar.initialState])] + list(tempGrammar.productions.items()))
        return tempGrammar

    def format_set(this, set_obj):
        label = "State {}\n".format_set(set_obj.state)
        for key, value in set_obj.productions.items():
            if key in set_obj.heart:
                label += "*** "
            production_str = ' | '.join(value)
            label += "{} -> {}\n".format_set(key, production_str)
        return label

    def compute_symbols(this, values):
        symbols = set()
        for production_set in values.productions.values():
            for production in production_set:
                parts = production.split()
                for part in parts:
                    if '.' in part:
                        symbol = part[1:] if part.startswith(
                            '.') else part.split()[0]
                        symbols.add(symbol)
        return list(symbols)

    def build_automata(this, firstSet):
        machine = Machine(firstSet.state, [0])
        unique_hearts = set()
        sets = [firstSet]
        unique_hearts.add(frozenset(firstSet.heart.items()))
        for set_obj in sets:
            symbols = this.compute_symbols(set_obj)
            for symbol in symbols:
                newSet = this.irA(set_obj, symbol)
                newSet_heart = frozenset(newSet.heart.items())
                if newSet_heart not in unique_hearts:
                    newSet.state = this.stateCount
                    this.stateCount += 1
                    sets.append(newSet)
                    unique_hearts.add(newSet_heart)
                    transition = Transition(set_obj, symbol, newSet)
                    machine.transitions.append(transition)
                else:
                    next_state_index = next(i for i, s in enumerate(sets) if frozenset(
                        s.heart.items()) == newSet_heart)
                    next_state = sets[next_state_index]
                    transition = Transition(set_obj, symbol, next_state)
                    machine.transitions.append(transition)
        graph = pydot.Dot(graph_type='digraph')
        for set_obj in sets:
            label = this.format_set(set_obj)
            node = pydot.Node(label)
            graph.add_node(node)
        for transition in machine.transitions:
            state = this.format_set(transition.state)
            next_state = this.format_set(transition.next)
            edge = pydot.Edge(state, next_state, label=transition.symbol)
            graph.add_edge(edge)
        for transition in machine.transitions[::-1]:
            if transition.state.state == 1:
                state = this.format_set(transition.state)
                next_state = 'accept'
                edge = pydot.Edge(state, next_state, label='$')
                graph.add_edge(edge)
                break
            elif transition.next.state == 1:
                state = this.format_set(transition.next)
                next_state = 'accept'
                edge = pydot.Edge(state, next_state, label='$')
                graph.add_edge(edge)
                break
        graph.write_pdf('LR0.pdf')
        machine.finalState = {'accept'}
        machine.display()
        this.result = machine
        return this.result
