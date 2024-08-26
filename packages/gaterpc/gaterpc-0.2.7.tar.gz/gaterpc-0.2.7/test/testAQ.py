# -*- coding: utf-8 -*-
# Author      : ShiFan
# Created Date: 2024/1/25 11:29
import asyncio

from gaterpc.global_settings import Settings
from gaterpc.utils import StreamReply


async def testp(sr):
    for i in range(10):
        await sr.asend(i)
    await sr.asend(Settings.STREAM_END_MESSAGE)


async def testg(sr):
    async for i in sr:
        print(f"get value: {i}")


async def test():
    loop = asyncio.get_event_loop()
    sr = StreamReply(maxsize=0, timeout=2)
    gt = loop.create_task(testg(sr))
    pt = loop.create_task(testp(sr))
    await gt
    await pt


def main():
    asyncio.run(test())


if __name__ == '__main__':
    main()
