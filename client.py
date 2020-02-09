import asyncio
import os
import aiohttp
from random import choice
from aiohttp import WSMsgType, WSMessage

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))
URL = f'http://{HOST}:{PORT}/client'

times = [3, 3, 3, 3, 3, 3, 3, 3, 3, 10]
res = ['ack', 'ack', 'ack', 'ack', 'ack',
       'ack', 'ack', 'ack', 'ack', 'rej']

LIMIT = 3
POSSIBLE_SUBS = [[1], [2], [3], [1, 2], [2, 3], [1, 3], [1, 2, 3]]

async def client(subs):
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:
        data = {
            'type': 'register',
            'subs': subs,
            'privileged': False
        }
        await ws.send_json(data)

        print('registered')

        handled = 0

        async for msg in ws:
            msg: WSMessage
            if msg.type == WSMsgType.TEXT:
                print('got task')
                await asyncio.sleep(choice(times))
                data = {
                    'type': choice(res)
                }
                print('processed')
                await ws.send_json(data)
                print('sent')

                # handled += 1
                # if handled >= LIMIT:
                #     resp = {
                #         'type': 'disconnect'
                #     }
                #     print('processed')
                #     await ws.send_json(resp)
                #     return


async def main():
    coros = [client(choice(POSSIBLE_SUBS)) for _ in range(12)]
    await asyncio.gather(*coros)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
