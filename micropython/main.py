FLASHING_PINS = [1,3]
MEMORY_PINS   = [6,7,8,9,10,11]

from machine import Pin
from time import sleep_ms
from _thread import start_new_thread

gates = []

def runGates():
    while True:
        sleep_ms(10)
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
    pin_num = int(pin)

    if pin_num in FLASHING_PINS:
        raise ValueError('Cannot use pins used for flashing or debugging.')
    elif pin_num in MEMORY_PINS:
        raise ValueError('Cannot use pins connected to flash memory.')

    elif mode==Pin.OUT:
        return Pin(pin_num, mode, value=value)
    else:
        return Pin(pin_num, mode)

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
                    if (count > 2) and (params[-2]=='='):
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
                                    gates.append((pinA, None, '=', setPin(params[2], Pin.OUT, value=pinA.value())))
                            print('OK')
                        
                        elif count == 5:        
                            if params[1]=='+':
                                "Set OR gate command"
                                pinA, pinB = setPin(params[0], Pin.IN), setPin(params[2], Pin.IN)
                                pinO = setPin(params[4], Pin.OUT, value=(pinA.value() or pinB.value()))

                                gates.append((pinA, pinB, '+', pinO))
                                print('OK')

                            else:
                                raise TypeError('Invalid Operator')
                        else:
                            raise SyntaxError('Invalid amount of parameters')
                else:
                    if count==1:
                        if (params[0]=='gates') and debug:
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
