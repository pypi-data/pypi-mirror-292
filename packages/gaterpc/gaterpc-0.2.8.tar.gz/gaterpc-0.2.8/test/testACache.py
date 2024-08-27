# -*- coding: utf-8 -*-
# Author      : ShiFan
# Created Date: 2024/2/28 16:10
import asyncio
import random
import time
from collections import deque
from functools import lru_cache
from uuid import uuid4

from gaterpc.utils import coroutine_lru_cache


A = uuid4().hex.encode("utf-8")
B = uuid4().hex.encode("utf-8")
C = uuid4().hex.encode("utf-8")
D = [
        [b"NULL", ],
        [b"PLAIN", b"testa", b"testap"],
        [b"PLAIN", b"testb", b"testbp"],
        [b"PLAIN", b"testc", b"testcp"],
        [b"PLAIN", b"testu", b"testp"],
    ]


class CacheCoroutine(object):
    def __init__(self, maxsize=128):
        self.maxsize = maxsize

    def __call__(self, coroutine):
        @lru_cache(maxsize=self.maxsize)
        def wrapper(*args, **kwargs) -> asyncio.Task:
            loop = asyncio.get_event_loop()
            t = loop.create_task(coroutine(*args, *kwargs))
            return t
        return wrapper


@coroutine_lru_cache
async def test_cache(a: bytes, b: bytes, c: bytes, *d: list) -> bool:
    await asyncio.sleep(2)
    hits = 0
    if a == A:
        print("hit A")
        hits += 1
    if b == B:
        print("hit B")
        hits += 1
    if c == C:
        print("hit C")
        hits += 1
    try:
        if d[0] == b"PLAIN" and d[1] == b"testu" and d[2] == b"testp":
            if hits == 3:
                print("hit D")
            return True
        else:
            return False
    except Exception:
        return False


async def atest():
    loop = asyncio.get_event_loop()
    ti = 0
    aws = deque()
    for i in range(3000):
        if not ti:
            a, b, c = A, B, C
            d = D[-1]
            ti = random.randint(1, 10)
        else:
            a = uuid4().hex.encode("utf-8")
            b = uuid4().hex.encode("utf-8")
            c = uuid4().hex.encode("utf-8")
            d = D[random.randint(0, 4)]
        ti -= 1
        aws.append(t := loop.create_task(test_cache(a, b, c, *d)))
        # t.add_done_callback(aws.remove)
    await asyncio.gather(*aws)
    print(test_cache.cache_info())


def main():
    asyncio.run(atest())


if __name__ == '__main__':
    main()
