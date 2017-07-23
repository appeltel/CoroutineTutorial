import time

def square(x):
    print('Starting square with argument {}!'.format(x))
    time.sleep(3)
    print('Finishing square with argument {}!'.format(x))
    return x * x

def cube(x):
    print('Starting cube with argument {}!'.format(x))
    time.sleep(3)
    y = square(x)
    print('Finishing cube with argument {}!'.format(x))
    return x * y
