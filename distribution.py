from typing import Dict, List, Tuple
from models import Task, Client, MetaQueues


meta_queues = List[MetaQueues]


def distribute(clients: Dict[str, Client], queues: Dict[int, List[Task]], meta_queues: List[MetaQueues]) -> List[Tuple[str, int, Task]]:

    for queue in queues:
        for client in clients:
            client: Client
            queue: List[Task]
            if client.


    return(List[Tuple[Client.uuid, int, Task]])
