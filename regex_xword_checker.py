#!/usr/bin/env python
""" A regular expression crossword checker for crosswords like the one
at http://boingboing.net/2013/02/11/regular-expressions-crossword.html

See README for more information.
"""

import re
import sys
import copy
try:
    import json
except ImportError:
    from simplejson import json

#: Constants to make it easier to deal with the three "dimensions" of
#: rules
L_TO_R = 0
BR_TO_TL = 1
TR_TO_BL = 2

RULE_TYPES = {"Left to right": L_TO_R,
              "Bottom-right to top-left": BR_TO_TL,
              "Top-right to bottom-left": TR_TO_BL}


def load_rules(fp):
    """ Load crossword ruleset from JSON data in the given file-like
    object """
    nonwords = re.compile(r'\W+')

    # build a dict of rule types without any non-word characters, so
    # we can freely compare the keys used in the JSON rule description
    # with the rule types without worrying about whether or not
    # someone forgot a space or a dash
    rule_types = dict([(nonwords.sub('', t).lower(), r)
                       for t, r in RULE_TYPES.items()])

    raw_rules = json.load(fp)
    compiled_rules = dict()
    for raw_rtype, rules in raw_rules.items():
        rtype = nonwords.sub('', raw_rtype).lower()
        if rtype == 'comment':
            continue
        if rtype not in rule_types:
            print("Skipping unknown rule type: %s" % raw_rtype)
            continue
        compiled_rules[rule_types[rtype]] = []
        for rule in rules:
            compiled_rules[rule_types[rtype]].append(re.compile('^%s$' % rule))
    for rdesc, rtype in RULE_TYPES.items():
        if rtype not in compiled_rules:
            print("Invalid ruleset: Missing %s rules" % rdesc)
            raise SystemExit(1)
    rule_lengths = [len(r) for r in compiled_rules.values()]
    if min(rule_lengths) != max(rule_lengths):
        print("Invalid ruleset: Not all dimensions have the same number of "
              "rules")
    return compiled_rules


def input_xword(rules):
    """ Get the crossword from user input """
    whitespace = re.compile(r'\s+')
    rv = []
    rows = len(rules[L_TO_R])
    edge_length = (rows + 1) / 2

    # figure out the correct input function for python 2/py3k
    try:
        input = raw_input  # pylint: disable=W0622
    except NameError:
        input = input

    print("Input crossword, one row at a time:")
    for i in range(rows):
        while True:
            if i < edge_length:
                line_length = i + edge_length
            else:
                line_length = rows - (i - (edge_length - 1))

            line = whitespace.sub('', input("%d: " % (i + 1))).upper()
            if len(line) != line_length:
                print "Invalid line, must be %d characters" % line_length
            else:
                rv.append(line)
                break
    return rv


def get_rows(xword, dim):
    """ Get a list of rows for the given rule 'dimension' """
    if dim == L_TO_R:
        return xword
    else:
        if dim == BR_TO_TL:
            padded = copy.copy(xword)
        else:
            padded = ["".join(reversed(line)) for line in xword]

        for i in range(len(xword[0])):
            padded[i] = " " * (len(xword[0]) - i - 1) + padded[i]

        if dim == BR_TO_TL:
            padded.reverse()

        rv = []
        for i in range(len(xword)):
            row = []
            for j in range(len(xword)):
                if len(padded[j]) <= i or padded[j][i] == ' ':
                    continue
                row.append(padded[j][i])
            rv.append("".join(row))
        return rv


def check_rows(xword, rules, dim):
    """ Check the rows in a given dimension """
    rows = get_rows(xword, dim)
    errors = []
    for i in range(len(xword)):
        if not rules[dim][i].match(rows[i]):
            errors.append(i)
    return errors


def red(val):
    """ Make a string display in red """
    return '\033[91m' + val + '\033[0m'


def display_crossword(xword, errors):
    """ Display the crossword, with errors highlighted in red """
    # first, convert each line to a list, so we can easily highlight
    # individual characters
    display = [list(line) for line in xword]

    for eline in errors[L_TO_R]:
        display[eline] = [red(char) for char in display[eline]]

    for eline in errors[TR_TO_BL]:
        # first half of the crossword
        char = len(xword) - eline - 1
        for line in range(max(0, len(xword[0]) - eline - 1), len(xword[0])):
            display[line][char] = red(display[line][char])

        # second half
        char = -1 - eline
        for line in range(len(xword[0]), len(xword)):
            if abs(char) > len(display[line]):
                break
            display[line][char] = red(display[line][char])

    for eline in errors[BR_TO_TL]:
        # first half of the crossword
        char = eline - len(xword)
        for line in range(max(0, len(xword[0]) - eline - 1), len(xword[0])):
            if abs(char) <= len(display[line]):
                display[line][char] = red(display[line][char])

        # second half of the crossword
        for line in range(len(xword[0]), len(xword)):
            char = eline - len(xword) + (line - len(xword[0])) + 1
            if char >= 0:
                break
            display[line][char] = red(display[line][char])

    for i in range(len(xword)):
        print("%s%s" % (" " * (len(xword) - len(display[i])),
                        "".join("%s " % c for c in display[i])))


def main():
    if len(sys.argv) == 2:
        fname = sys.argv[1]
    else:
        fname = "rules.json"
    try:
        rules = load_rules(open(fname))
    except IOError:
        print("Could not open rules file %s: %s" % (rules, sys.exc_info()[1]))

    xword = input_xword(rules)
    errors = dict()
    for dim in [L_TO_R, BR_TO_TL, TR_TO_BL]:
        errors[dim] = check_rows(xword, rules, dim)
    num_errors = sum(len(e) for e in errors.values())
    if num_errors:
        print("Found %d errors" % num_errors)
    else:
        print("Correct!")
    if sys.stdout.isatty():
        display_crossword(xword, errors)
    return num_errors


if __name__ == '__main__':
    sys.exit(main())
