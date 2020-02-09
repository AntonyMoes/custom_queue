from aiohttp.web import WebSocketResponse
from dataclasses import dataclass
from typing import List


@dataclass
class Task:
    uuid: str
    id: int
    time: float
    started_processing: float
    payload: str
    assignee: str = None


@dataclass
class Client:
    uuid: str
    ws: WebSocketResponse
    subs: List[int]
    last_task_time: float
    privileged: bool = False
    task: Task = None
