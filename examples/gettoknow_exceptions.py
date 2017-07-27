import asyncio

async def square(x):
    print('Starting square with argument {}!'.format(x))
    if x == 7:
        raise ValueError("Can't square 7 - I'm not very good at this :(")
    await asyncio.sleep(3)
    print('Finishing square with argument {}!'.format(x))
    return x * x

async def list_squares(n):
    coros = []
    for idx in range(n):
        coros.append(square(idx))

    results = await asyncio.gather(*coros, return_exceptions=True)
    return results
