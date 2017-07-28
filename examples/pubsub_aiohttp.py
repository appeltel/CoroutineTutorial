import asyncio
from aiohttp import web


class Hub():

    def __init__(self):
        self.subscriptions = set()

    def publish(self, message):
        for queue in self.subscriptions:
            queue.put_nowait(message)


class Subscription():

    def __init__(self, hub):
        self.hub = hub
        self.queue = asyncio.Queue()

    def __enter__(self):
        hub.subscriptions.add(self.queue)
        return self.queue

    def __exit__(self, type, value, traceback):
        hub.subscriptions.remove(self.queue)


hub = Hub()


async def sub(request):
    resp = web.StreamResponse()
    resp.headers['content-type'] = 'text/plain'
    resp.status_code = 200
    await resp.prepare(request)
    with Subscription(hub) as queue:
        while True:
            msg = await queue.get()
            resp.write(bytes(f'{msg}\r\n', 'utf-8'))
    return resp


async def pub(request):
    msg = request.query.get('msg', '')
    hub.publish(msg)
    return web.Response(text='ok')


if __name__ == '__main__':
    app = web.Application()
    app.router.add_get('/', sub)
    app.router.add_post('/', pub)
    web.run_app(app)
