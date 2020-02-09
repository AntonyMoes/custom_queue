from aiohttp.web import WebSocketResponse
from dataclasses import dataclass
from typing import List


@dataclass
class Task:
    uuid: str
    id: int
    time: float
    payload: str
    assignee: str = None


@dataclass
class Client:
    uuid: str
    ws: WebSocketResponse
    subs: List[int]
    last_task_time: float
    ready: bool = True
    privileged: bool = False
