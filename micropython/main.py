FLASHING_PINS = [1,3]
MEMORY_PINS   = [6,7,8,9,10,11]

from machine import Pin
import _thread, time

gates = []

def runGates():
    while True:
      for (pinA , pinB, op, pinO) in gates:
          if   op=='+':
              pinO.value((pinA.value() or pinB.value()))
          elif op=='*':
              pinO.value((pinA.value() and pinB.value()))
          elif op=='!':
              pinO.value(not pinA.value())
      time.sleep(1)

def pinSafetyCheck(pin:int):
    if pin in FLASHING_PINS:
        raise ValueError('Cannot use pins used for flashing or debugging.')
    elif pin in MEMORY_PINS:
        raise ValueError('Cannot use pins connected to flash memory.')

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
                            pin = int(params[0])
                            pinSafetyCheck(pin)

                            state = params[2]=='x'
                            p = Pin(pin, Pin.IN if state else Pin.OUT)
                            if not state:
                                if   params[2]=='1':
                                    p.on()
                                elif params[2]=='0':
                                    p.off()
                                else:
                                    raise TypeError("Can only set pin to 1, 0 or X")
                            print('OK')
                        
                        elif count == 5:        
                            if params[1]=='+':
                                "Set OR gate command"
                                a, b, o = int(params[0]), int(params[2]), int(params[4])
                                pinSafetyCheck(a)
                                pinSafetyCheck(b)
                                pinSafetyCheck(o)
                                
                                pinA, pinB = Pin(a, Pin.IN), Pin(b, Pin.IN)
                                pinO = Pin(o, Pin.OUT, value=(pinA.value() or pinB.value()))

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
    _thread.start_new_thread(runGates, ())
    print()
    main()
