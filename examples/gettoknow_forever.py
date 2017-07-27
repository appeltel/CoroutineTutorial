import asyncio

async def stop_in(n):
    loop = asyncio.get_event_loop()
    while n > 0:
        print('Shutdown in {}...'.format(n))
        await asyncio.sleep(1)
        n = n - 1

    loop.stop()
