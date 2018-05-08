from itertools import cycle, islice
from unify import unify, find, UnifyException
from classes import Variable

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

class Model:
    def __init__(self, state):
        self.state = state

    def __eq__(self, other):
        return Equals(self, other)
    
    def __and__(self, other):
        return Conj(self, other)
    
    def __or__(self, other):
        return Disj(self, other)

    def run(self, subst={}):
        raise NotImplementedError()


class Disj(Model):
    def __init__(self, g1, g2):
        self.state = None
        self.g1 = g1
        self.g2 = g2
        super().__init__(self.state)

    def run(self, subst={}):
        return stream_append(self.g1.run(subst), self.g2.run(subst))


class Conj(Model):
    def __init__(self, g1, g2):
        self.state = None
        self.g1 = g1
        self.g2 = g2
        super().__init__(self.state)

    def run(self, subst={}):
        return stream_map(self.g2.run, self.g1.run(subst))
                
class Equals(Model):
    def __init__(self, g1, g2):
        self.state = None
        if isinstance(g1, Model):
            g1 = g1.state
        if isinstance(g2, Model):
            g2 = g2.state

        if g1 is None or g2 is None:
            raise NotImplementedError()
            
        self.g1 = g1
        self.g2 = g2
        super().__init__(self.state)

    def run(self, subst={}):
        try:                    
            s = unify(find(self.g1, subst),
                      find(self.g2, subst), subst)
            yield s
        except UnifyException:
            return []

def extract(subst, key):
    if isinstance(key, Model) and isinstance(key.state, Variable):
        return find(key.state, subst)
    else:
        return subst[key]
    
def var(name):
    v = Variable(name)
    return Model(v)
