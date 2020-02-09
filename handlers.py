from uuid import uuid1
import asyncio
from aiohttp import WSMsgType, WSMessage
from aiohttp.web import WebSocketResponse, json_response
from time import time
from models import Task, Client, QueueStats
from distribution import distribute, distribute1
from utils import log, add_stats
from pprint import pprint


def mock_distribute(app, client):
    if len(app['queues'][1]) > 0:
        task = app['queues'][1].pop(0)
        send(app, client.uuid, task)


def apply_distribution(app):
    distribution = distribute1(app['clients'], app['queues'])
    pprint(distribution)
    for uuid, task in distribution:
        send(app, uuid, task)


TIMEOUT = 5


async def timeout(app, task_uuid: str):
    await asyncio.sleep(TIMEOUT)
    if task_uuid in app['pending']:
        task = app['pending'][task_uuid]

        # in case task was reassigned
        if time() - task.started_processing >= TIMEOUT - 0.1:
            add_stats(app, task, successfull=False)

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
    task.started_processing = time()

    async def helper(client: Client, task: Task):
        try:
            await client.ws.send_json({
                'status': 'ok',
                'type': 'task',
                'payload': task.payload
            })
            print('sent')
            asyncio.get_running_loop().create_task(timeout(app, task.uuid))

        except BaseException as e:
            # TODO: handle
            print('EXCEPTION', e)
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
            apply_distribution(app)
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
                    apply_distribution(app)
                    # mock_distribute(app, client)

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

                    send(app, client.uuid, task)

                log(app)

            elif data['type'] == 'ack':
                task_uuid = client.task
                client.last_task_time = time()
                if task_uuid is not None:
                    task = app['pending'][task_uuid]
                    del app['pending'][task_uuid]
                    client.task = None

                    add_stats(app, task, successfull=True)

                if not client.privileged:
                    apply_distribution(app)
                    # mock_distribute(app, client)

                log(app)

            elif data['type'] == 'rej':
                task_uuid = client.task
                client.last_task_time = time()
                if task_uuid is not None:
                    task = app['pending'][task_uuid]
                    del app['pending'][task_uuid]
                    app['queues'][task.id].insert(0, task)
                    client.task = None
                    task.assignee = None

                    add_stats(app, task, successfull=False)

                    task.started_processing = None

                log(app)

                if not client.privileged:
                    apply_distribution(app)
                    # mock_distribute(app, client)

                log(app)

            elif data['type'] == 'disconnect':
                if client.task is not None:
                    pending: Task = app['pending'][client.task]
                    del app['pending'][client.task]
                    pending.assignee = None

                    add_stats(app, pending, successfull=False)

                    pending.started_processing = None
                    app['queues'][pending.id].insert(0, pending)

                del app['clients'][client.uuid]

                log(app)

            else:
                assert False

    return ws


async def stat_handle(request):
    app = request.app

    stats = {
        'queues': {s_id: s.__dict__ for s_id, s in app['stats']['queues'].items()},
        'num_clients': len(app['clients']),
        'num_working_clients': len([c for c in app['clients'].values() if c.task is not None])
    }
    pprint(stats)
    for q_id, queue in app['queues'].items():
        q_stats = stats['queues'].get(q_id)
        if q_stats is not None:
            q_stats['len'] = len(queue)

    stats['queues'] = list(stats['queues'].values())

    return json_response(stats)
