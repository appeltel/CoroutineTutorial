import asyncio

async def square(x):
    print('Starting square with argument {}!'.format(x))
    await asyncio.sleep(3)
    print('Finishing square with argument {}!'.format(x))
    return x * x

async def launch_square(x):
    loop = asyncio.get_event_loop()
    task = loop.create_task(square(x))
    while not task.done():
        print('waiting for square({})...'.format(x))
        await asyncio.sleep(1)

    return task.result()
