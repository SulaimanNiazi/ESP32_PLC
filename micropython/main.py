from config import FLASHING_PINS, MEMORY_PINS, OPERATOR_ORDER
from machine import Pin, reset, soft_reset, lightsleep, deepsleep
from time import sleep_us
from _thread import start_new_thread
from ujson import dump, load

logics  = []
outputs = []

class Logic:
    def __init__(self, equation, output):        
        self.pins = []
        self.inputs = []
        self.layers = layer = 0
        self.eq = equation
        equation = [""] + equation + [""]
        size = len(equation) - 1
        
        for ind in range(1,size):
            prev, current, next = equation[ind-1:ind+2]
            
            if current.isdigit(): 
                if current not in self.pins:
                    if current == output: raise ValueError("Value Error: Cannot directly connect the output pin to any input pin.")
                    if next.isdigit(): raise SyntaxError("Syntax Error: Cannot use more than one Pin value without a logic gate.")
                    if next == "(" or prev == ")": raise SyntaxError(f"Syntax Error: Cannot place brackets right next to a pin value ({current}) without a logic gate in between.")

                    pin = setPin(current, Pin.IN)
                    self.pins.append(pin)
                    self.inputs.append(current)
        
            elif current in OPERATOR_ORDER:
                if current == "!":
                    if prev.isdigit() or prev == ")": raise SyntaxError(f"Syntax Error: A pin value '{prev}' was found before NOT gate '!' symbol")
                    if next in (")", ""): raise SyntaxError("Syntax Error: NOT gate needs a pin value or open brackets after it.")
                else:
                    if next in (')', '') or prev in ('(', ''): raise SyntaxError(f"Syntax Error: '{current}' Symbol needs a pin value or brackets before and after it.")

            elif current == "(":
                self.layers += 1
                layer += 1
            elif current == ")":
                layer -= 1

                if prev == "(": raise SyntaxError("Syntax Error: Cannot leave brackets empty.")
                if next == "(": raise SyntaxError("Syntax Error: Cannot place more than one pair of brackets without a logic gate.")
                if layer < 0: raise SyntaxError("Syntax Error: Unopened brackets found.")
            else: raise SyntaxError(f"Syntax Error: Unknown parameter '{current}' found.")
        if layer > 0: raise SyntaxError("Syntax Error: Unclosed brackets found.")
        
        self.output = setPin(output, Pin.OUT)
    
    def update(self):
        def solve(eq, layers=0):
            def subSolve(param1, op, param2="0"):
                val1, val2 = int(param1), int(param2)
                if   op == "+": val = val1 or val2
                elif op == "*": val = val1 and val2
                elif op == "^": val = val1 ^ val2
                elif op == "!": val = not val1
                else: val = val1
                return str(val)
            
            while layers:
                ind2 = eq.index(")")
                ind1 = ind2 - list(reversed(eq[:ind2+1])).index("(")
                eq = eq[:ind1] + solve(eq[ind1+1:ind2]) + eq[ind2+1:]
                layers-=1
            
            for ind in range(len(eq)-1, -1, -1):
                if eq[ind] == "!":
                    eq.pop(ind)
                    val = int(eq[ind])
                    eq[ind] = "0" if val else "1"
            
            for op in OPERATOR_ORDER[1:]:
                for ind in range(len(eq)-2, -1, -1):
                    if eq[ind+1]==op:
                        param1 = eq.pop(ind+2)
                        sign = eq.pop(ind+1)
                        eq[ind] = subSolve(eq[ind], sign, param1)
            return eq

        eq = self.eq
        for id, pin in zip(self.inputs, self.pins):
            value = str(pin.value())
            eq = [value if p==id else p for p in eq]
        self.output.value(int(solve(eq, self.layers)[0]))

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
                    if count == 1: display(f"{Pin(int(params[0])).value()}")

                    elif params[1] == '=':
                        if count == 3 and params[2] == 'x': 
                            setPin(params[0], Pin.IN, force=True)
                        else:
                            if output in outputs: raise ValueError(f"Value Error: Pin {output} is already the output of a boolean expression. Set pin as input to free it.")
                            logic = Logic(params[2:], params[0])
                            logics.append(logic)
                            outputs.append(params[0])
                        display('OK')

                    else: raise SyntaxError(f'Syntax Error: "=" is expected as the second parameter, not "{params[1]}".')
                else:
                    def ensureCount(ensured):
                        if count != ensured:
                            ensured -= 1
                            raise SyntaxError(f"Syntax Error: {params[0].upper()} command " + (f"requires {ensured} {"parameters" if ensured > 1 else "parameter"}." if ensured else "does not support any parameters."))

                    if count == 0: raise SyntaxError('No command entered.')                    
                    elif params[0] == "list":
                        ensureCount(1)
                        display('\n'.join(f'{logic.output} = ' + ' '.join(f'Pin({p})' if p.isdigit() else p for p in logic.eq) for logic in logics) if logics else 'NONE')
                    
                    elif params[0] == "help":
                        ensureCount(1)
                        try:
                            with open('README.txt', 'r') as f: display("OK\n" + f.read())
                        except OSError: raise FileNotFoundError("File Not Found Error: README.txt is missing or corrupted.")
                    
                    elif params[0] == "save":
                        ensureCount(1)
                        data = [(logic.eq, out) for logic, out in zip(logics, outputs)]
                        with open("backup.json", "w") as f: dump(data, f)
                        display("OK")

                    elif params[0] == "set":
                        ensureCount(2)
                        setPin(params[1], Pin.OUT, 1)
                        display("OK")

                    elif params[0] == "reset":
                        ensureCount(2)
                        if params[1].isdigit(): 
                            setPin(params[1], Pin.OUT, 0)
                            display("OK")
                        elif params[1] == "soft": soft_reset()
                        elif params[1] == "hard": reset()
                        else: raise ValueError(f"Value Error: RESET command does not recognise '{params[1]}' parameter.")
                    
                    elif params[0] == "sleep":
                        ensureCount(3)
                        if params[2].isdigit():
                            time = int(params[2])
                            if params[1] == "light":
                                display("OK")
                                lightsleep(time)
                            elif params[1] == "deep":
                                display("OK")
                                deepsleep(time)
                            else: raise ValueError(f"Value Error: '{params[1]}' is an invalid parameter for SLEEP command.")
                        else: raise ValueError(f"Value Error: SLEEP command's 2nd parameter should be numeric.")
                    else: raise SyntaxError(f"Syntax Error: '{params[0]}' is an unrecognized command.")
            except Exception as e: display(e if debug else "?")
        else: print(output)

def keepSolving():
    while True:
        sleep_us(1)
        for logic in logics: logic.update()

if __name__ == "__main__":
    start_new_thread(keepSolving, ())
    try:
        with open("backup.json", "r") as f: backup = load(f)
        for d in backup:
            logics.append(Logic(d[0], d[1]))
            outputs.append(d[1])
    finally: main()
