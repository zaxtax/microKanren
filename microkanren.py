from collections import Sequence


def stream_append(x, y, subst):
    while True:
        if isinstance(x, Relation):
            x, y = y, x.force()
        elif isinstance(y, Relation):
            y = y.force()
        elif isinstance(x, Model):
            x = x.run(subst)
        else:
            try:
                yield next(x)
                y, x = x, y
            except StopIteration:
                if isinstance(y, Model):
                    y = y.run(subst)
                for i in y:
                    yield i
                return


def stream_map(constraint, s):
    subst = next(s)
    yield from stream_append(constraint(subst),
                             stream_map(constraint, s),
                             subst)


def id_eq(x, y):
    return id(x) == id(y)


class Model:
    def __eq__(self, other):
        return Equals(self, other)

    def __and__(self, other):
        return Conj(self, other)

    def __rand__(self, other):
        return Conj(other, self)

    def __or__(self, other):
        return Disj(self, other)

    def __ror__(self, other):
        return Disj(other, self)

    def add(self, other):
        "Convienence function"
        self = Conj(self, other)
        return self

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
        return stream_append(self.g1, self.g2, subst)


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
        return id_eq(x, u)
    if isinstance(u, (tuple, list)):
        return any(occurs(x, find(i, subst), subst)
                   for i in u)
    return False


def find(x, subst):
    if x in subst:
        return find(subst[x], subst)
    else:
        return x


def ground(x, subst):
    if x in subst:
        return ground(subst[x], subst)
    elif isinstance(x, list):
        return [ground(i, subst) for i in x]
    elif isinstance(x, tuple):
        return tuple(ground(i, subst) for i in x)
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


class Relation(Model):
    def __init__(self, g):
        self.g = g

    def force(self):
        for i in self.g:
            return i

    def run(self, subst={}):
        "Convienence function"
        return self.force().run(subst)


def relational(f):
    def delay(*args):
        yield f(*args)

    def wrap(*args):
        return Relation(delay(*args))

    return wrap
