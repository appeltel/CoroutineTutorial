import asyncio

import aiohttp

BASE_URL = 'https://ericappelt.com/animals/'


async def speak(animal, session):

    async with session.get('{}/{}'.format(BASE_URL, animal)) as response:
        response.raise_for_status()
        sound = await response.text()

    return 'The {} says "{}".'.format(animal, sound)


async def main():
    animals = ['cow', 'pig', 'chicken']
    coroutines = []
    async with aiohttp.ClientSession() as session:
        for animal in animals:
            coro = speak(animal, session)
            coroutines.append(coro)

        responses = await asyncio.gather(*coroutines)

    for line in responses:
        print(line)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
