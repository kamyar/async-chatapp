import asyncio

from aiohttp import web
from aiohttp import WSMsgType as MsgType
import aiohttp_jinja2
import jinja2

class ChatList(web.View):
    @aiohttp_jinja2.template('chat/index.html')
    async def get(self):
        return {}

class WebSocket(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        self.request.app['user_counter'] += 1
        user_id = self.request.app['user_counter']
        for _ws in self.request.app['websockets']:
            _ws.send_str('%s joined' % user_id)
        self.request.app['websockets'].append(ws)

        async for msg in ws:
            if msg.tp == MsgType.text:
                if msg.data == 'close':
                    await ws.close()
                else:
                    for _ws in self.request.app['websockets']:
                        _ws.send_str('(%s) %s' % (user_id, msg.data))
            elif msg.tp == MsgType.error:
                print('ws connection closed with exception %s' % ws.exception())

        self.request.app['websockets'].remove(ws)
        for _ws in self.request.app['websockets']:
            _ws.send_str('%s disconected' % user_id)
        print('websocket connection closed')

        return ws

app = web.Application()
app['websockets'] = []
app['user_counter'] = 0

app.router.add_get('/ws', WebSocket)
app.router.add_get('/', ChatList)
app.router.add_static('/static', 'static', name='static')
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))


async def periodic():
    while True:
        for _ws in app['websockets']:
            _ws.send_str('O, you are still here! Nice :)')
        print("------- Sending Periodic Message -------")
        await asyncio.sleep(10)


asyncio.ensure_future(periodic())

loop = asyncio.get_event_loop()
web.run_app(app, port=8080)
