from microkanren import var, relational, Equals


@relational
def anyo(g):
    return g | anyo(g)


def make_cons(start, stop=None):
    if stop is None:
        start, stop = 0, start
    if start == stop:
        return ()
    else:
        return (start, make_cons(start+1, stop))


@relational
def append(l, s, o):
    a = var("a")
    d = var("d")
    r = var("r")
    return ((Equals(l, ()) & Equals(s, o)) |
            (Equals(l, (a, d)) &
             Equals(o, (a, r)) &
             append(d, s, r)))


x = var('x')
q = var('q')
body = (x == q) & (x == 3)

for solution in body.run():
    print(solution[q])
