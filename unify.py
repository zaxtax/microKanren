from collections import Sequence
from classes import Variable

class UnifyException(Exception):
    pass

def occurs(x, u, subst):
    if isinstance(u, Variable):
        return x == u
    if isinstance(u, (tuple, list)):
        return any(occurs(x, find(i, subst), subst)
                   for i in u)
    return False


def find(x, subst):
    if x in subst:
        return find(subst[x], subst)
    else:
        return x


def extend_subst(x, v, subst):
    if occurs(x, v, subst):
        raise UnifyException(f"{x} occurs in {v}")
    else:
        subst = subst.copy()
        subst[x] = v
        return subst


def unify(x, y, subst):
    if x == y:
        return subst
    if isinstance(x, Variable):
        return extend_subst(x, y, subst)
    if isinstance(y, Variable):
        return unify(y, x, subst)
    if (isinstance(x, Sequence) and
        isinstance(y, Sequence) and
        len(x) == len(y)):
        for i, j in zip(x, y):
            subst = unify(find(i, subst), find(j, subst), subst)
        return subst
    raise UnifyException(f"Failed to unify {x} and {y}")
