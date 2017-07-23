import types

@types.coroutine
def manual_sleep(n):
    yield "Please do not continue until {} seconds have elapsed.".format(n)


async def square(x):
    print('Starting square with argument {}!'.format(x))
    await manual_sleep(3)
    print('Finishing square with argument {}!'.format(x))
    return x * x

async def cube(x):
    print('Starting cube with argument {}!'.format(x))
    await manual_sleep(3)
    y = await square(x)
    print('Finishing cube with argument {}!'.format(x))
    return x * y
