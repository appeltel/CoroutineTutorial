import asyncio
import time

async def square(x):
    print('Starting square with argument {}!'.format(x))
    if x == 7:
        raise ValueError("Can't square 7 - I'm not very good at this :(")
    await asyncio.sleep(3)
    print('Finishing square with argument {}!'.format(x))
    return x * x

def blocking_square(x):
    print('Starting blocking square with argument {}!'.format(x))
    time.sleep(3)
    print('Finishing blocking square with argument {}!'.format(x))
    return x * x

async def list_squares(n):
    loop = asyncio.get_event_loop()
    coros = []
    for idx in range(n):
        if idx == 7:
            coro = loop.run_in_executor(None, blocking_square, idx)
            coros.append(coro)
        else:
            coros.append(square(idx))

    results = await asyncio.gather(*coros, return_exceptions=True)
    return results
