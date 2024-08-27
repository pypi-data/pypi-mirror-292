import asyncio
import json
import threading

import aiohttp

from maitai._config import config
from maitai_common.version import version


class MaitaiClient:

    def __init__(self):
        super().__init__()

    @classmethod
    def run_async(cls, coro):
        """
        Modified helper method to run coroutine in a background thread if not already in an asyncio loop,
        otherwise just run it. This allows for both asyncio and non-asyncio applications to use this method.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # No running event loop
            loop = None

        if loop and loop.is_running():
            # We are in an asyncio loop, schedule coroutine execution
            asyncio.create_task(coro, name='maitai')
        else:
            # Not in an asyncio loop, run in a new event loop in a background thread
            def run():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                new_loop.run_until_complete(coro)
                new_loop.close()

            threading.Thread(target=run).start()

    @classmethod
    def log_error(cls, error: str, path: str):
        cls.run_async(cls.increment_error(error, path))

    @classmethod
    async def increment_error(cls, error: str, path: str):
        host = config.maitai_host
        url = f'{host}/metrics/increment/python_sdk_error'
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': config.api_key,
            'x-client-version': version,
        }
        labels = {
            "cause": error,
            "type": "ERROR",
            "path": path,
        }
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                return await session.put(url, headers=headers, data=json.dumps(labels))
        except:
            pass
