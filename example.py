from microkanren import var, extract

x = var('x')
q = var('q')
body = (x == q) & (x == 3)

res = body.run()
for solution in res:
    print(extract(solution, q))
