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
            'privileged': False
        }
        await ws.send_json(data)

        print('registered')

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

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
