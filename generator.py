import asyncio
import os
import aiohttp
from time import sleep
from random import choice


HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))
URL = f'http://{HOST}:{PORT}/generator'

# SLEEP = 3
IDS = [1, 2, 3]
SLEEPS = [2.8, 3.0, 3.2]


async def generator(id):
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:
        while True:
            data = {
                'id': id,
                'payload': 'stuff'
            }
            await ws.send_json(data)
            await asyncio.sleep(choice(SLEEPS))


async def main():
    coros = [generator(choice(IDS)) for _ in range(10)]
    await asyncio.gather(*coros)


if __name__ == '__main__':
    sleep(5)
    asyncio.get_event_loop().run_until_complete(main())
