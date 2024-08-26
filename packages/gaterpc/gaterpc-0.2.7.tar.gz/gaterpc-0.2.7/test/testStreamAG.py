# -*- coding: utf-8 -*-
# Author      : ShiFan
# Created Date: 2024/3/13 15:29
import asyncio

from gaterpc.global_settings import Settings
from gaterpc.utils import StreamReply, throw_exception_agenerator


async def aiterator(ag):
    try:
        async for i in ag:
            print(i)
            await asyncio.sleep(0.5)
    except Exception as error:
        print(error)


async def throw(ag):
    await throw_exception_agenerator(ag, RuntimeError("test exception"))


async def main():
    Settings.setup()
    ag = StreamReply(
        Settings.STREAM_END_MESSAGE,
        timeout=3
    )
    at = asyncio.create_task(aiterator(ag))
    for i in range(10):
        if i == 5:
            await throw(ag)
        await ag.asend(i)
    await asyncio.sleep(0.1)
    await ag.asend(Settings.STREAM_END_MESSAGE)
    await at


if __name__ == '__main__':
    asyncio.run(main())
