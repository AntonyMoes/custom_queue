import asyncio
import os
import aiohttp
from random import choice
from aiohttp import WSMsgType, WSMessage

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))
URL = f'http://{HOST}:{PORT}/client'

times = [3, 3, 3, 10]
res = ['ack', 'ack', 'ack', 'rej']


async def main():
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:
        data = {
            'type': 'register',
            'subs': [1],
            'privileged': True
        }
        await ws.send_json(data)

        print('registered')

        q_id = 1

        data = {
            'type': 'get_list',
            'query': q_id
        }
        await ws.send_json(data)

        print('task list requested')

        async for msg in ws:
            msg: WSMessage
            if msg.type == WSMsgType.TEXT:
                data = msg.json()
                print(data)
                if data['status'] == 'err':
                    await asyncio.sleep(5)
                    data = {
                        'type': 'get_list',
                        'query': q_id
                    }
                    await ws.send_json(data)
                    print('task list requested again')

                if data['type'] == 'task':
                    print('got task')
                    await asyncio.sleep(choice(times))
                    resp = {
                        'type': choice(res)
                    }
                    print('processed')
                    await ws.send_json(resp)
                    print('sent')

                    resp = {
                        'type': 'disconnect'
                    }
                    await ws.send_json(resp)
                    return

                elif data['type'] == 'task_list':
                    print('got task list')
                    tasks = data['tasks']
                    if len(tasks) == 0:
                        await asyncio.sleep()
                        data = {
                            'type': 'get_list',
                            'query': q_id
                        }
                        await ws.send_json(data)
                        print('task list requested again')

                    task = choice(tasks)
                    resp = {
                        'type': 'get',
                        'id': q_id,
                        'task': task
                    }
                    await ws.send_json(resp)
                    print('task requested')

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
