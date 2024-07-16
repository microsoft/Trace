from opto import trace

x = trace.node(1)
y = 2

ops = ['+', '-', '*', '/', '//', '%', '**', '<<', '>>', '&', '|', '^']

for op in ops:
    exec(f"assert x {op} y == x.data {op} y")
    exec(f"assert y {op} x == y {op} x.data ")
