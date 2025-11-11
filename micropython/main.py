FLASHING_PINS = [1,3]
MEMORY_PINS   = [6,7,8,9,10,11]

from machine import Pin
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
            elif op=='=':
                pinO.value(pinA.value())

def setPin(pin:str, mode:int, value=None):
    id = int(pin)

    if id in FLASHING_PINS:
        raise ValueError('Cannot use pins used for flashing or debugging.')
    elif id in MEMORY_PINS:
        raise ValueError('Cannot use pins connected to flash memory.')

    if mode==Pin.OUT:
        return Pin(id, mode, value=value)
    else:
        for (pinA , pinB, op, pinO) in gates:
            pin_name = f'{pinO}'
            pin_id = pin_name[pin_name.find('(')+1:pin_name.find(')')]
            if pin_id==pin:
                gates.remove((pinA , pinB, op, pinO))
                break
        return Pin(id, mode)
    
def setGate(in1:str, in2:str, op:str, out:str):
    pinA, pinB, pinO = setPin(in1, Pin.IN), setPin(in2, Pin.IN) if in2 else None, setPin(out, Pin.OUT)
    newGate = (pinA, pinB, op, pinO)
    
    if (newGate in gates) or ((pinB, pinA, op, pinO) in gates):
        raise ValueError('Gate already exists.')
    elif pinA==pinO or pinB==pinO:
        raise ValueError('Output pin cannot be the same as input pin(s).')
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
            debug = params[-1]=='?'
            if debug:
                params.pop()
            count = len(params)
            
            try:
                if line[0].isdigit():
                    if count > 2 and params[1]=='=':
                        "Set Commands"
                        if count == 3:
                            "Set Pin Command"
                            if params[2]=='x':
                                setPin(params[0], Pin.IN)
                            else:
                                pinA = setPin(params[0], Pin.OUT)
                                num = int(params[2])
                                if num in (0,1):
                                    pinA.value(num)
                                else:
                                    setGate(params[2], None, '=', params[0])
                            print('OK')
                        
                        elif count == 5:        
                            if params[3]=='+':
                                "Set OR gate command"
                                setGate(params[4], params[2], '+', params[0])
                                print('OK')

                            else:
                                raise TypeError('Invalid Operator')
                        else:
                            raise SyntaxError('Invalid amount of parameters')
                    else:
                        raise SyntaxError('Invalid syntax')
                else:
                    if count==1:
                        if params[0]=='gates' and debug:
                            print("OK",f"\n{gates}")

                        else:
                            raise ValueError('Invalid value')
                    else:
                        raise SyntaxError('Invalid amount of parameters')
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
