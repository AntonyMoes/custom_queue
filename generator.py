import asyncio
import os
import aiohttp

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))
URL = f'http://{HOST}:{PORT}/generator'

SLEEP = 2
ID = 1


async def main():
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:
        while True:
            data = {
                'id': ID,
                'payload': 'stuff'
            }
            await ws.send_json(data)
            await asyncio.sleep(SLEEP)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
