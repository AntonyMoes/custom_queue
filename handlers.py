from uuid import uuid1
import asyncio
from aiohttp import WSMsgType, WSMessage
from aiohttp.web import WebSocketResponse
from time import time
from models import Task, Client
from distribution import distribute


async def lel():
    await asyncio.sleep(1)
    print('lel')


async def generator_handle(request) -> WebSocketResponse:
    ws = WebSocketResponse()
    await ws.prepare(request)
    app = request.app

    async for msg in ws:
        msg: WSMessage
        if msg.type == WSMsgType.TEXT:
            data = msg.json()
            task = Task(**data, time=time(), uuid=str(uuid1()))
            print(task)

            if task.id not in app['queues']:
                app['queues'][id] = []

            app['queues'][id].append(task)
            await distribute(app['clients'], app['queues'])

    return ws


async def client_handle(request) -> WebSocketResponse:
    ws = WebSocketResponse()
    await ws.prepare(request)
    app = request.app

    uuid = None
    async for msg in ws:
        msg: WSMessage
        if msg.type == WSMsgType.TEXT:
            data = msg.json()
            if data['type'] == 'register':
                uuid = str(uuid1())
                app['clients'][uuid] = Client(uuid=uuid, ws=ws, subs=data['subs'],
                                              last_task_time=time(), privileged=data['privileged'])
            elif data['type'] == 'get_list':
                pass  # TODO

            elif data['type'] == 'get':
                pass  # TODO

            elif data['type'] == 'ack':
                pass  # TODO

            elif data['type'] == 'rej':
                pass  # TODO

            elif data['type'] == 'disconnect':
                pass  # TODO

            else:
                assert False

    return ws