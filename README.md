# microKanren
python implementation of µKanren

## Short example

````python
from microkanren import var

x = var('x')
q = var('q')
body = (x == q) & (x == 3)

for solution in body.run():
    print(solution[q])

````
