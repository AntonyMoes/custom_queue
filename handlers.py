from uuid import uuid1
from aiohttp import WSMsgType, WSMessage
from aiohttp.web import WebSocketResponse
from time import time
from dataclasses import dataclass
from typing import List


@dataclass
class Task:
    uuid: str
    id: int
    time: float
    payload: str
    assignee: int = None


@dataclass
class Client:
    uuid: str
    ws: WebSocketResponse
    subs: List[int]
    last_task_time: float
    ready: bool = True


async def generator_handle(request) -> WebSocketResponse:
    ws = WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        msg: WSMessage
        if msg.type == WSMsgType.TEXT:
            data = msg.json()
            task = Task(**data, time=time())

            print(task)

    return ws
