from typing import Dict, List, Tuple
from models import Task, Client
from time import time


def distribute(clients: Dict[str, Client], queues: Dict[int, List[Task]]) -> List[Tuple[str, int, Task]]:
    released_list = []

    for q_id, queue in queues.items():
        active = list(filter(lambda c: q_id in c.subs, clients.values()))
        client: Client
        queue: List[Task]
        for c_id, client in active:
            client.task = queue[0]
            client.last_task_time = time()
            queue.pop(0)
            released_list.append(Tuple[client.uuid, q_id, client.task])

    return released_list
