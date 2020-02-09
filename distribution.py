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


def distribute1(clients: Dict[str, Client], queues: Dict[int, List[Task]]) -> List[Tuple[str, Task]]:
    released_list = []
    available_queues = queues
    active: Dict[str, Client] = {i: c for i, c in clients.items() if c.task is None and not c.privileged}

    while len(active) > 0 and len(available_queues) > 0:
        tasks = list(sorted(map(lambda q: q[0], filter(lambda q: len(q) > 0, available_queues.values())), key=lambda t: t.time))
        if len(tasks) == 0:
            return released_list

        oldest = tasks[0]

        available = list(sorted(filter(lambda c: oldest.id in c.subs, active.values()), key=lambda c: c.last_task_time))
        if len(available) == 0:
            del available_queues[oldest.id]
            continue

        client = available[0]
        del active[client.uuid]
        queues[oldest.id].pop(0)

        released_list.append((client.uuid, oldest))

    return released_list
