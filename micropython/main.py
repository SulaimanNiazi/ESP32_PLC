FLASHING_PINS  = (1, 3)
MEMORY_PINS    = (6, 7, 8, 9, 10, 11)

OPERATOR_ORDER = ('!', '*', '^', '+')

from machine import Pin, reset
from time import sleep_us
from _thread import start_new_thread

class Logic:
    def __init__(self, equation, output):
        if output in outputs: raise ValueError(f'Pin {output} is already the output of a logical expression. Set pin as input to free it.')
        
        self.eq = equation
        self.pins = []
        self.inputs = []
        self.layers = layer = 0
        size = len(equation)
        gate = False
        
        for ind in range(size):
            current = equation[ind]
            next = equation[ind+1] if ind < size-1 else ''
            prev = equation[ind-1] if ind > 0 else ''
            
            if current.isdigit(): 
                if current not in self.pins:
                    if current == output: raise ValueError('Value Error: Cannot directly connect the output pin to any input pin.')
                    if next.isdigit(): raise SyntaxError('Syntax Error: Cannot use more than one Pin value without a logic gate.')
                    if next == '(' or prev == ')': raise SyntaxError(f'Syntax Error: Cannot place brackets right next to a pin value ({current}) without a logic gate in between.')

                    pin = setPin(current, Pin.IN)
                    self.pins.append(pin)
                    self.inputs.append(current)
        
            elif current in OPERATOR_ORDER:
                if current == '!':
                    if next in (')', None): raise SyntaxError('Syntax Error: NOT gate needs a pin value or open brackets after it.')
                else:
                    if next in (')', '') or prev in ('(', ''): raise SyntaxError(f"Syntax Error: '{current}' Symbol needs a pin value or brackets before and after it.")

            elif current == '(':
                self.layers += 1
                layer += 1
            elif current == ')':
                layer -= 1

                if prev == '(': raise SyntaxError('Syntax Error: Cannot leave brackets empty.')
                if next == '(': raise SyntaxError('Syntax Error: Cannot place more than one pair of brackets without a logic gate.')
                if layer < 0: raise SyntaxError("Syntax Error: Unopened brackets found.")
            else: raise SyntaxError(f"Syntax Error: Unknown parameter '{current}' found.")
        if layer > 0: raise SyntaxError("Syntax Error: Unclosed brackets found.")
        
        self.output = setPin(output, Pin.OUT)
        outputs.append(output)

logics = []
outputs = []

def solve(eq, layers=0):
    def subSolve(param1, op, param2='0'):
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
            for id, pin in zip(logic.inputs, logic.pins):
                value = str(pin.value())
                eq = [value if p==id else p for p in eq]
            logic.output.value(int(solve(eq, logic.layers)[0]))

def setPin(pin, mode, value=0, force=False):
    id = int(pin)

    if id in FLASHING_PINS: raise ValueError('Value Error: This pin is used for flashing or debugging.')
    elif id in MEMORY_PINS: raise ValueError('Value Error: This pin is connected to flash memory.')

    if mode == Pin.OUT: return Pin(id, mode, value=value)
    else:
        try: 
            ind = outputs.index(pin)
            if force: 
                logics.pop(ind)
                outputs.pop(ind)
            else: return Pin(id, Pin.OUT)
        finally: return Pin(id, mode)

def main():
    output = '?'
    def display(text):
        nonlocal output
        output=text
        print(output)

    while True:
        entry = input('\n> ').lower().strip()
        if entry:
            params = [p for p in entry.split(' ') if p]
            debug = params[-1] == '?'
            if debug: params.pop()
            count = len(params)
            
            try:
                if entry[0].isdigit():
                    if count == 1: display(f'OK\n{Pin(int(params[0])).value()}')

                    elif params[1] == '=':
                        if count == 3 and params[2] == 'x': 
                            setPin(params[0], Pin.IN, force=True)
                        else:
                            logic = Logic(params[2:], params[0])
                            logics.append(logic)
                        display('OK')

                    else: raise SyntaxError(f'Syntax Error: "=" is expected as the second parameter, not "{params[1]}".')
                else:
                    if count == 0: raise SyntaxError('No command entered.')

                    elif count == 1:
                        if params[0] == 'list':
                            output = '\n'.join(f'{logic.output} = ' + ' '.join(f'Pin({p})' if p.isdigit() else p for p in logic.eq) for logic in logics) if logics else 'NONE'
                            display('OK\n' + output)

                        elif params[0] == 'reset':
                            print('OK')
                            reset()

                        elif params[0] == 'help':
                            with open('README.txt', 'r') as f: display("OK\n" + f.read())

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
    main()
