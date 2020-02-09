from uuid import uuid1
import asyncio
from aiohttp import WSMsgType, WSMessage
from aiohttp.web import WebSocketResponse
from time import time


async def lel():
    await asyncio.sleep(1)
    print('lel')


async def generator_handle(request) -> WebSocketResponse:
    ws = WebSocketResponse()
    await ws.prepare(request)
    print(request.app)

    async for msg in ws:
        msg: WSMessage
        if msg.type == WSMsgType.TEXT:
            data = msg.json()
            task = Task(**data, time=time(), uuid=str(uuid1()))

            print(task)
            # asyncio.get_running_loop().create_task(lel())

    return ws
