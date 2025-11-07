FLASHING_PINS = [1,3]
MEMORY_PINS   = [6,7,8,9,10,11]

from machine import Pin

def main():
    while True:
        line = input('> ').lower().strip()
        
        if line:
            if line[0].isdigit():
                params = line.split(' ')
                debug = params[-1]=='?'
                if debug:
                    params.pop()
                count = len(params)
                
                if (params[1]=='=') and (count == 3):
                    "Set Command"
                    try:
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
                    except Exception as e:
                        print(e)
                        print('?')
                        
                else:
                    print('?')
            else:
                print('?')

def pinSafetyCheck(pin:int):
    if pin in FLASHING_PINS:
        raise ValueError('Cannot use pins used for flashing or debugging.')
    elif pin in MEMORY_PINS:
        raise ValueError('Cannot use pins connected to flash memory.')
    
if __name__ == '__main__':
    print()
    main()
