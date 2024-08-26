"""Module to hold helper functions."""

import inflect

p = inflect.engine()

def is_singular(word):
    return word == p.singular_noun(word) or not p.singular_noun(word)

def singular(word):
    return word if not p.singular_noun(word) else p.singular_noun(word)
def plural(word):
    return p.plural(word)
