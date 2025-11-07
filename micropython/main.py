from machine import Pin

def main():
    while True:
        line = input('> ').lower().strip()
        if line[0].isdigit():
            params = line.split(' ')
            
            if (len(params) == 3) and (params[1]=='='):
                try:
                    pin = int(params[0])
                    state = params[2]=='x'

                    p = Pin(pin, Pin.IN if state else Pin.OUT)
                    if not state:
                        if params[2]=='1':
                            p.on()
                        elif params[2]=='0':
                            p.off()
                        else:
                            print('?')
                except:
                    print('?')
            else:
                print('?')
        else:
            print('?')

if __name__ == '__main__':
    print()
    main()
