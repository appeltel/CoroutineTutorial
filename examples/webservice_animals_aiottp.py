from asyncio import sleep

from aiohttp import web

FARM = {
    'cow': 'Moo!',
    'pig': 'Oink!',
    'sheep': 'Baaa!',
    'chicken': 'Cluck!',
    'bird': 'Tweet!',
    'duck': 'Quack!',
    'dog': 'Woof!',
    'cat': 'Meow!',
    'frog': 'Ribbit!',
    'horse': 'Neigh!',
    'turkey': 'Gobble-Gobble!',
    'rooster': 'Cock-a-Doodle-Doo!'
}


async def hello(request):
    msg = 'Welcome to the farm!'
    return web.Response(text=msg)


async def speak(request):
    animal = request.match_info['name']
    if animal not in FARM:
        return web.Response(
            text='The animal {0} was not found.'.format(animal),
            status=404
        )

    await sleep(5)
    return web.Response(text=FARM[animal])


app = web.Application()
app.router.add_get('/animals', hello)
resource = app.router.add_resource('/animals/{name}')
resource.add_route('GET', speak)

web.run_app(app)
