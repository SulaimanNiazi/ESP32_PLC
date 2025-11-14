FLASHING_PINS  = (1,3)
MEMORY_PINS    = (6,7,8,9,10,11)

OPERATOR_ORDER = ('!', '*', '^', '+')

from machine import Pin, reset
from time import sleep_us
from _thread import start_new_thread

class Logic:
    def __init__(self, exp):
        self.eq = exp[2:]
        self.inputs = []
        self.ids = []
        self.layers = layer = 0
        
        for p in self.eq:
            if p == '(': 
                self.layers += 1
                layer += 1
            elif p == ')':
                layer -= 1
                if layer < 0: raise SyntaxError("Syntax Error: Unopened brackets found.")
            elif p.isdigit() and p not in self.inputs: 
                pin = setPin(p, Pin.IN)
                self.inputs.append(pin)
                self.ids.append(p)
            elif p not in OPERATOR_ORDER: raise SyntaxError(f"Syntax Error: Unknown parameter '{p}' found.")
        if layer > 0: raise SyntaxError("Syntax Error: Unclosed brackets found.")

        self.output = setPin(exp[0], Pin.OUT)

logics = []

def solve(eq, layers=0):
    def subSolve(param1:str, op:str, param2:str='0'):
        val1, val2 = int(param1), int(param2)
        if   op == '+': val = val1 or val2
        elif op == '*': val = val1 and val2
        elif op == '^': val = val1 ^ val2
        elif op == '!': val = not val1
        else: val = val1
        return str(val)
    
    while layers:
        ind2 = eq.index(')')
        ind1 = ind2 - list(reversed(eq[:ind2+1])).index('(')
        eq = eq[:ind1] + solve(eq[ind1+1:ind2]) + eq[ind2+1:]
        layers-=1
    
    for ind in range(len(eq)-1, -1, -1):
        if eq[ind] == '!':
            eq.pop(ind)
            val = int(eq[ind])
            eq[ind] = '0' if val else '1'
    
    for op in OPERATOR_ORDER[1:]:
        for ind in range(len(eq)-2, -1, -1):
            if eq[ind+1]==op:
                param1 = eq.pop(ind+2)
                sign = eq.pop(ind+1)
                eq[ind] = subSolve(eq[ind], sign, param1)
    return eq

def keepSolving():
    while True:
        sleep_us(1)
        for logic in logics:
            eq = logic.eq
            # if Pin(2, Pin.IN).value():
            #     print(logic.ids)
            #     print(logic.inputs)
            for id, pin in zip(logic.ids, logic.inputs):
                value = str(pin.value())
                eq = [value if p==id else p for p in eq]
            logic.output.value(int(solve(eq, logic.layers)[0]))

def setPin(pin:str, mode:int, value:int=0, force:bool=False):
    id = int(pin)

    if id in FLASHING_PINS: raise ValueError('Value Error: This pin is used for flashing or debugging.')
    elif id in MEMORY_PINS: raise ValueError('Value Error: This pin is connected to flash memory.')

    if mode == Pin.OUT: return Pin(id, mode, value=value)
    else:
        for logic in logics:
            if f'{logic.output}'==f'Pin({id})': 
                if force: 
                    logics.remove(logic)
                    break
                else: return Pin(id, Pin.OUT)
        return Pin(id, mode)
    
# def setGate(in1:str, in2:str, op:str, out:str, inv:bool=False):
#     global gates
#     pinA, pinB, pinO = setPin(in1, Pin.IN), setPin(in2, Pin.IN) if in2 else None, setPin(out, Pin.OUT)
#     gate = (pinA, pinB, op, pinO, inv)
    
#     if (gate in gates) or ((pinB, pinA, op, pinO, inv) in gates): raise ValueError('Value Error: This gate already exists.')
#     elif pinO in (pinA, pinB): raise ValueError('Value Error: Cannot directly connect the output pin to any input pin.')
#     else: gates = [g for g in gates if g[3] != pinO]
    
#     gates.append(gate)

def main():
    output = '?'

    def display(text:str):
        nonlocal output
        output=text
        print(output)

    while True:
        entry = input('> ').lower().strip()
        if entry:
            params = [p for p in entry.split(' ') if p]
            debug = params[-1] == '?'

            if debug: params.pop()
            
            count = len(params)
            
            try:
                if entry[0].isdigit():
                    if count == 1: display(f'OK\n{Pin(int(params[0])).value()}')

                    elif params[1] == '=':
                        logic = Logic(params)
                        logics.append(logic)
                        print('OK')

                    else: raise SyntaxError(f'Syntax Error: "=" is expected as the second parameter, not "{params[1]}".')
                else:
                    if count == 0: raise SyntaxError('No command entered.')

                    elif count == 1:
                        if params[0] == 'list':
                            if not logics: display('OK\nNONE')
                            else:
                                line = 'OK\n'
                                for logic in logics:
                                    eq = "".join(f'{p} ' for p in logic.eq)
                                    line += f'{logic.output} = ' + eq + '\n'
                                display(line)

                        elif params[0] == 'reset':
                            print('OK')
                            reset()

                        elif params[0] == 'help':
                            with open('README.txt', 'r') as f: print("OK\n" + f.read())

                        else: raise SyntaxError(f'Syntax Error: "{params[0]}" is an unknown command.')
                    
                    elif count == 2:
                        if params[1].isdigit():
                            pin = setPin(params[1], Pin.OUT)
                            if   params[0] == 'set'  : pin.value(1)
                            elif params[0] == 'reset': pin.value(0)

                            else: raise SyntaxError(f'Syntax Error: "{params[0]}" is an unknown command.')
                            
                            display('OK')
                    
                    else: raise SyntaxError(f'Syntax Error: The entered value "{params[0]}" does not take {count} parameters.')
            except Exception as e: display(e if debug else '?')
        else: print(output)

if __name__ == '__main__':
    start_new_thread(keepSolving, ())
    print()
    main()
