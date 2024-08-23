from pylogics_modalities.parsers import parse_pltl
from pylogics_modalities.syntax.base import (
    And as PLTLAnd,
    Or as PLTLOr,
    Formula,
    Implies as PLTLImplies,
    Not as PLTLNot
)
from pylogics_modalities.syntax.pltl import (
    Atomic as PLTLAtomic,
    Before,
    WeakBefore,
    Historically,
    Once
)
from typing import Set


def past_simple_env(formula: Set[PLTLAtomic]) -> Formula:
    or_u = None
    not_and = None
    for u1 in formula:
        if or_u == None:
            or_u = u1
            and_neg_u = PLTLNot(u1)
        else:
            or_u = PLTLOr(or_u, u1)
            and_neg_u = PLTLAnd(and_neg_u, PLTLNot(u1))
        for u2 in formula:
            if not u1.__eq__(u2):
                if not_and == None:
                    not_and = PLTLNot(PLTLAnd(u1, u2))
                else:
                    not_and = PLTLAnd(not_and, PLTLNot(PLTLAnd(u1, u2)))

    phi2 = PLTLImplies(Before(or_u), and_neg_u)
    phi3 = PLTLImplies(Before(Before(or_u)), or_u)
    left = Once(PLTLAnd
                (WeakBefore(parse_pltl("false")), or_u))
    if len(formula) == 1:
        phi1 = PLTLImplies(or_u, parse_pltl("true"))
    else:
        phi1 = PLTLImplies(or_u, not_and)
    right = Historically(
        PLTLAnd(phi1, phi2, phi3))

    return PLTLAnd(left, right)


def past_simple_con(formula: Set[PLTLAtomic]) -> Formula:
    or_c = None
    not_and_c = None
    for c1 in formula:
        if or_c == None:
            or_c = c1
            and_neg_c = PLTLNot(c1)
            and_c = c1
        else:
            or_c = PLTLOr(or_c, c1)
            and_neg_c = PLTLAnd(and_neg_c, PLTLNot(c1))
            and_c = PLTLAnd(and_c, c1)
        for c2 in formula:
            if not c1.__eq__(c2):
                if not_and_c == None:
                    not_and_c = PLTLNot(PLTLAnd(c1, c2))
                else:
                    not_and_c = PLTLAnd(not_and_c, PLTLNot(PLTLAnd(c1, c2)))
    if len(formula) == 1:
        phi1 = PLTLImplies(Before(and_neg_c), or_c)
    else:
        phi1 = PLTLImplies(Before(and_neg_c), PLTLAnd(or_c, not_and_c))
    phi2 = PLTLImplies(Before(Before(and_neg_c)), and_neg_c)
    right = Historically(PLTLAnd(phi1, phi2))

    left = Once(PLTLAnd
                (WeakBefore(parse_pltl("false")), and_neg_c))

    return PLTLAnd(left, right)


'''
# Examples:
formula_str = "!a S H(a)"  # should be modifies to  ( !a S (false T a))
print(formula_str)
formula_pltl = parse_pltl(formula_str)
print(formula_pltl)
formula_modified = modify(formula_pltl)  # (since (not a) (triggers false a))
print(formula_modified)

formula_str = "O a"  # should be modifies to  (true S a)
print(formula_str)
formula_pltl = parse_pltl(formula_str)
print(formula_pltl)
# (since PropositionalTrue(Logic.PLTL) a)
formula_modified = modify(formula_pltl)
print(formula_modified)

'''
