FLASHING_PINS = [1,3]
MEMORY_PINS   = [6,7,8,9,10,11]

from machine import Pin, reset
from time import sleep_us
from _thread import start_new_thread

gates = []

def runGates():
    while True:
        sleep_us(1)
        for (pinA , pinB, op, pinO) in gates:
            if   op=='+':
                pinO.value((pinA.value() or pinB.value()))
            elif op=='*':
                pinO.value((pinA.value() and pinB.value()))
            elif op=='!':
                pinO.value(not pinA.value())
            elif op=='^':
                pinO.value(pinA.value() ^ pinB.value())
            elif op=='':
                pinO.value(pinA.value())

def setPin(pin:str, mode:int, value=None, force:bool=False):
    id = int(pin)

    if id in FLASHING_PINS:
        raise ValueError('Value Error: This pin is used for flashing or debugging.')
    elif id in MEMORY_PINS:
        raise ValueError('Value Error: This pin is connected to flash memory.')

    if mode==Pin.OUT:
        return Pin(id, mode, value=value)
    else:
        for (pinA , pinB, op, pinO) in gates:
            pinO_name = f'{pinO}'
            pinO_id = pinO_name[pinO_name.find('(')+1:pinO_name.find(')')]
            if pinO_id==pin:
                if force:
                    gates.remove((pinA , pinB, op, pinO))
                    break
                else:
                    return Pin(id, Pin.OUT)
        return Pin(id, mode)
    
def setGate(in1:str, in2:str, op:str, out:str):
    pinA, pinB, pinO = setPin(in1, Pin.IN), setPin(in2, Pin.IN) if in2 else None, setPin(out, Pin.OUT)
    newGate = (pinA, pinB, op, pinO)
    
    if (newGate in gates) or ((pinB, pinA, op, pinO) in gates):
        raise ValueError('Value Error: This gate already exists.')
    elif pinA==pinO or pinB==pinO:
        raise ValueError('Value Error: Cannot directly connect the output pin to any input pin.')
    else:
        for (oldPinA , oldPinB, oldOp, oldPinO) in gates:
            if oldPinO==pinO:
                gates.remove((oldPinA , oldPinB, oldOp, oldPinO))
                break
    gates.append(newGate)

def main():
    while True:
        line = input('> ').lower().strip()
        if line:
            params = line.split(' ')
            
            for param in params:
                if not param:
                    params.remove(param)

            debug = params[-1]=='?'
            if debug:
                params.pop()
            
            count = len(params)
            
            try:
                if line[0].isdigit():
                    if count == 1:
                        "Read Pin Command"
                        print(f'OK\n{Pin(int(params[0])).value()}')

                    elif params[1]=='=':
                        "Set Commands"
                        if count == 3:
                            "Set Pin Command"
                            if params[2]=='x':
                                setPin(params[0], Pin.IN, force=True)
                            else:
                                pinA = setPin(params[0], Pin.OUT)
                                num = int(params[2])
                                if num in (0,1):
                                    pinA.value(num)
                                else:
                                    setGate(params[2], None, '', params[0])
                            print('OK')

                        elif count == 4:
                            if params[2]=='!':
                                "Set NOT gate command"
                                setGate(params[3], None, '!', params[0])
                                print('OK')

                            else:
                                raise SyntaxError(f'Syntax Error: "!" is expected as the operator for a gate with one input, not "{params[2]}".')
                        
                        elif count == 5:        
                            if params[3]=='+':
                                "Set OR gate command"
                                setGate(params[4], params[2], '+', params[0])
                                print('OK')
                            elif params[3]=='*':
                                "Set AND gate command"
                                setGate(params[4], params[2], '*', params[0])
                                print('OK')
                            elif params[3]=='^':
                                "Set XOR gate command"
                                setGate(params[4], params[2], '^', params[0])
                                print('OK')

                            else:
                                raise TypeError(f'Type Error: "{params[3]}" is an invalid operator for a gate with two inputs.')
                        else:
                            raise SyntaxError(f'Syntax Error: {count} parameters are {"too less" if (count<3) else "too many"} for a set command.')
                    else:
                        raise SyntaxError(f'Syntax Error: "=" is expected as the second parameter, not "{params[1]}".')
                else:
                    if count==0:
                        raise SyntaxError('No command entered.')
                    elif count==1:
                        if params[0]=='gates':
                            print('OK')
                            if not gates:
                                print('NONE')
                            else:
                                for (pinA , pinB, op, pinO) in gates:
                                    print(f'{pinO} = {pinA} {op} {pinB}' if pinB else f'{pinO} = {op}{pinA}')
                        elif params[0]=='reset':
                            print('OK')
                            reset()
                        elif params[0]=='help':
                            print('OK')
                            print("""
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
> 13 = 1
OK
> 15
OK
1
> GATES
OK
Pin(15) = Pin(12) + Pin(13)
> 15 = x
> gates
OK
NONE
> reset
OK
                                  """)

                        else:
                            raise ValueError(f'Value Error: "{params[0]}" is an unknown command.')
                    else:
                        raise SyntaxError(f'Syntax Error: The entered value "{params[0]}" does not take {count} parameters.')
            except Exception as e:
                if debug:
                    print(e)
                else:
                    print('?')
        else:
            print('?')

if __name__ == '__main__':
    start_new_thread(runGates, ())
    print()
    main()
