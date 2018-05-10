from itertools import cycle, islice
from collections import Sequence

def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it) for it in iterables)
    while pending:
        try:
            for g in nexts:
                yield next(g)
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

def stream_append(*streams):
    return roundrobin(*streams)

def stream_map(constraint, s):
    for i in s:
        for j in constraint(i):
            yield j

def id_eq(x, y):
    return id(x) == id(y)

class Model:
    def __eq__(self, other):
        return Equals(self, other)

    def __and__(self, other):
        return Conj(self, other)

    def __or__(self, other):
        return Disj(self, other)

    def run(self, subst={}):
        raise NotImplementedError()

class Variable(Model):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return object.__hash__(self)

class Equals(Model):
    def __init__(self, g1, g2):
        self.g1 = g1
        self.g2 = g2
        super().__init__()

    def run(self, subst={}):
        try:
            s = unify(find(self.g1, subst),
                      find(self.g2, subst), subst)
            yield s
        except UnifyException:
            return []

class Disj(Model):
    def __init__(self, g1, g2):
        self.g1 = g1
        self.g2 = g2
        super().__init__()

    def run(self, subst={}):
        return stream_append(self.g1.run(subst), self.g2.run(subst))


class Conj(Model):
    def __init__(self, g1, g2):
        self.g1 = g1
        self.g2 = g2
        super().__init__()

    def run(self, subst={}):
        return stream_map(self.g2.run, self.g1.run(subst))

class UnifyException(Exception):
    pass

def occurs(x, u, subst):
    if isinstance(u, Variable):
        return id_eq(x, y)
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
    if id_eq(x, y):
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

def var(name):
    return Variable(name)

def relational(f):
    def delay(*args):
        yield f(*args)
    return delay

@relational
def anyo():
    return (x == 1) | anyo()

def force(x):
    for i in x:
        return i
