import random

def get(pin):
    val = random.randrange(2)
    print(f'{pin} = {val}')
    return str(val)

def solve(eq:list[str]):
    def subSolve(param1:str, op:str, param2:str='0'):
        val1, val2 = int(param1), int(param2)
        if   op == '+': val = val1 or val2
        elif op == '*': val = val1 and val2
        elif op == '^': val = val1 ^ val2
        elif op == '!': val = not val1
        else: val = val1
        return str(val)
    
    for ind in range(len(eq)-1, -1, -1):
        if eq[ind] == '!':
            eq.pop(ind)
            val = int(eq[ind])
            eq[ind] = '0' if val else '1'
    for op in ('*', '^', '+'):
        for ind in range(len(eq)-2, -1, -1):
            if eq[ind+1]==op:
                param1 = eq.pop(ind+2)
                sign = eq.pop(ind+1)
                eq[ind] = subSolve(eq[ind], sign, param1)
    return eq

entry = input('> ')

params = [p for p in entry.split(' ') if p]

eq = params[2:]

layers = eq.count('(')

if layers != eq.count(')'): raise SyntaxError('Bracket Error')
else: print('layers:', layers)

# Replace with input readings
inputs = list(set([p for p in eq if p not in ('*', '+', '^', '!', '(', ')')]))

for param in inputs: 
    value = get(param)
    eq = [value if p==param else p for p in eq]

print(eq)

while layers:
    ind2 = eq.index(')')
    ind1 = ind2 - list(reversed(eq[:ind2+1])).index('(')
    eq = eq[:ind1] + solve(eq[ind1+1:ind2]) + eq[ind2+1:]
    layers-=1

print(solve(eq))
