FLASHING_PINS = [1,3]
MEMORY_PINS   = [6,7,8,9,10,11]

from machine import Pin, reset
from time import sleep_us
from _thread import start_new_thread

gates = []

def runGates():
    while True:
        sleep_us(1)
        for (pinA, pinB, op, pinO, inv) in gates:
            if   op == '+': val = pinA.value() or pinB.value()
            elif op == '*': val = pinA.value() and pinB.value()
            elif op == '^': val = pinA.value() ^ pinB.value()
            elif op == '' : val = pinA.value()
            if inv: val = not val
            pinO.value(val)

def setPin(pin:str, mode:int, value:int=0, force:bool=False):
    id = int(pin)

    if id in FLASHING_PINS: raise ValueError('Value Error: This pin is used for flashing or debugging.')
    elif id in MEMORY_PINS: raise ValueError('Value Error: This pin is connected to flash memory.')

    if mode == Pin.OUT: return Pin(id, mode, value=value)
    else:
        for gate in gates:
            if f'{gate[3]}'==f'Pin({id})': 
                if force: 
                    gates.remove(gate)
                    break
                else: return Pin(id, Pin.OUT)
        return Pin(id, mode)
    
def setGate(in1:str, in2:str, op:str, out:str, inv:bool=False):
    global gates
    pinA, pinB, pinO = setPin(in1, Pin.IN), setPin(in2, Pin.IN) if in2 else None, setPin(out, Pin.OUT)
    gate = (pinA, pinB, op, pinO, inv)
    
    if (gate in gates) or ((pinB, pinA, op, pinO, inv) in gates): raise ValueError('Value Error: This gate already exists.')
    elif pinO in [pinA, pinB]: raise ValueError('Value Error: Cannot directly connect the output pin to any input pin.')
    else: gates = [g for g in gates if g[3] != pinO]
    
    gates.append(gate)

def main():
    while True:
        line = input('> ').lower().strip()
        if line:
            params = [p for p in line.split(' ') if p != '']
            debug = params[-1] == '?'

            if debug: params.pop()
            
            count = len(params)
            
            try:
                if line[0].isdigit():
                    if count == 1: print(f'OK\n{Pin(int(params[0])).value()}')

                    elif params[1] == '=':
                        inv = params[2] == '!'
                        if inv:
                            count -= 1
                            params.pop(2)

                        if count == 3:
                            if params[2] == 'x': setPin(params[0], Pin.IN, force=True)
                            else:
                                pinA = setPin(params[0], Pin.OUT)
                                num = int(params[2])
                                pinA.value(num) if num in (0,1) else setGate(params[2], None, '', params[0], inv)

                        elif count == 5:
                            if params[3] in ['+', '*', '^']: setGate(params[4], params[2], params[3], params[0], inv) 

                            else: raise TypeError(f'Type Error: "{params[3]}" is an invalid operator for a gate.')
                        else: raise SyntaxError(f'Syntax Error: {count} parameters are {"too less" if (count<3) else "too many"} for a set command.')
                        print('OK')
                    else: raise SyntaxError(f'Syntax Error: "=" is expected as the second parameter, not "{params[1]}".')
                else:
                    if count == 0: raise SyntaxError('No command entered.')

                    elif count == 1:
                        if params[0] == 'gates':
                            print('OK')
                            if not gates: print('NONE')
                            else:
                                for (pinA, pinB, op, pinO, inv) in gates:
                                    eq = f'{pinA}'
                                    if pinB: eq += f' {op} {pinB}'
                                    print(f'{pinO} = ' + (f'! ({eq})' if inv else eq))

                        elif params[0] == 'reset':
                            print('OK')
                            reset()

                        elif params[0] == 'help':
                            print("""OK
# Pin Safety

The following pins are **protected** to prevent interference with flash memory or serial programming:

| Type         | Pins |
| ------------ | ---- |
| Flash/Debug  | 1, 3 |
| Flash Memory | 6-11 |

Any attempt to use these pins will result in an error.
Furthermore:
- Directly shorting the gates inputs and outputs or duplicating gates will result in error.
- Overwriting output pins will result in the deletion/replacement of gates.
- Add `?` at the end of any command for **debug mode** to show detailed error messages.

# Example Session

> 15 = 12 + 13
OK
> 14 = ! 12 + 13
OK
> 13 = 1
OK
> 15
OK
1
> GATES
OK
Pin(15) = Pin(12) + Pin(13)
Pin(14) = !(Pin(12) + Pin(13))
> 15 = x
OK
> 14 = x
OK
> gates
OK
NONE
> reset
OK
                                  """)

                        else: raise ValueError(f'Value Error: "{params[0]}" is an unknown command.')
                    else: raise SyntaxError(f'Syntax Error: The entered value "{params[0]}" does not take {count} parameters.')
            except Exception as e: print(e if debug else '?')
        else: print('?')

if __name__ == '__main__':
    start_new_thread(runGates, ())
    print()
    main()
