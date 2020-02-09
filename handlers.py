from uuid import uuid1
import asyncio
from aiohttp import WSMsgType, WSMessage
from aiohttp.web import WebSocketResponse
from time import time
from models import Task, Client
from distribution import distribute
from utils import log


def mock_distribute(app, client):
    if len(app['queues'][1]) > 0:
        task = app['queues'][1].pop(0)
        send(app, client.uuid, task)


TIMEOUT = 5


async def timeout(app, task_uuid: str):
    await asyncio.sleep(TIMEOUT)
    if task_uuid in app['pending']:
        task = app['pending'][task_uuid]

        # in case task was reassigned
        if time() - task.started_processing >= TIMEOUT - 0.1:
            task.started_processing = None
            del app['pending'][task_uuid]
            app['queues'][task.id].insert(0, task)
            app['clients'][task.assignee].task = None

            print(f'TIMEOUT FOR TASK {task_uuid}')

            log(app)


def send(app, client_uuid: str, task: Task):
    client: Client = app['clients'][client_uuid]
    # TODO: add client validity checks

    task.assignee = client.uuid
    app['pending'][task.uuid] = task
    client.task = task.uuid

    async def helper(client: Client, task: Task):
        try:
            await client.ws.send_json({
                'status': 'ok',
                'type': 'task',
                'payload': task.payload
            })
            task.started_processing = time()
            asyncio.get_running_loop().create_task(timeout(app, task.uuid))

        except BaseException as e:
            # TODO: handle
            pass

    asyncio.get_running_loop().create_task(helper(client, task))


async def generator_handle(request) -> WebSocketResponse:
    ws = WebSocketResponse()
    await ws.prepare(request)
    app = request.app

    async for msg in ws:
        msg: WSMessage
        if msg.type == WSMsgType.TEXT:
            data = msg.json()
            task = Task(**data, time=time(), uuid=str(uuid1()), started_processing=None)
            print(task)

            if task.id not in app['queues']:
                app['queues'][task.id] = []

            app['queues'][task.id].append(task)

            log(app)

            # todo: add distribution
            # to_send = distribute(app['clients'], app['queues'])

    return ws


async def client_handle(request) -> WebSocketResponse:
    ws = WebSocketResponse()
    await ws.prepare(request)
    app = request.app

    client = None
    async for msg in ws:
        msg: WSMessage
        if msg.type == WSMsgType.TEXT:
            data = msg.json()
            print(f'TYPE: {data["type"]}')

            if data['type'] == 'register':
                uuid = str(uuid1())
                client = Client(uuid=uuid, ws=ws, subs=data['subs'],
                                last_task_time=time(), privileged=data['privileged'])
                app['clients'][uuid] = client

                if not client.privileged:
                    # TODO: distribute
                    mock_distribute(app, client)

                log(app)

            elif data['type'] == 'get_list':
                if not client.privileged:
                    assert False

                q_id = data['query']
                tasks = list(map(lambda t: t.uuid, app['queues'][q_id]))

                resp = {
                    'status': 'ok',
                    'type': 'task_list',
                    'tasks': tasks,
                }
                await client.ws.send_json(resp)

            elif data['type'] == 'get':
                if not client.privileged:
                    assert False

                q_id = data['id']
                task_uuid = data['task']
                tasks = list(filter(lambda t: t.uuid == task_uuid, app['queues'][q_id]))
                if len(tasks) < 1:
                    await client.ws.send_json({
                        'status': 'err'
                    })
                else:
                    task = tasks[0]
                    app['queues'][q_id] = list(filter(lambda t: t.uuid != task_uuid, app['queues'][q_id]))

                    # todo: REFACTOR SEND
                    # client.task = task.uuid
                    # task.assignee = client.uuid
                    # app['pending'][task.uuid] = task

                    send(app, client.uuid, task)

                log(app)

            elif data['type'] == 'ack':
                task_uuid = client.task
                client.last_task_time = time()
                if task_uuid is not None:
                    del app['pending'][task_uuid]
                    client.task = None

                if not client.privileged:
                    # TODO: distribute
                    mock_distribute(app, client)

                log(app)

            elif data['type'] == 'rej':
                task_uuid = client.task
                client.last_task_time = time()
                if task_uuid is not None:
                    task = app['pending'][task_uuid]
                    del app['pending'][task_uuid]
                    task.started_processing = None
                    app['queues'][task.id].insert(0, task)
                    client.task = None

                log(app)

                if not client.privileged:
                    # TODO: distribute
                    mock_distribute(app, client)

                log(app)

            elif data['type'] == 'disconnect':
                if client.task is not None:
                    pending: Task = app['pending'][client.task]
                    del app['pending'][client.task]
                    pending.assignee = None
                    pending.started_processing = None
                    app['queues'][pending.id].insert(0, pending)

                del app['clients'][client.uuid]

                log(app)

            else:
                assert False

    return ws