# -*- coding: utf-8 -*-
# Author      : ShiFan
# Created Date: 2024/8/15 11:12
import asyncio
import os
import selectors
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Optional

import _posixshmem


base_path = Path(__file__).parent
sys.path.append(base_path.parent.as_posix())
from gaterpc.utils import (
    UnixEPollEventLoopPolicy, msg_pack, msg_unpack,
    run_in_executor, to_bytes,
)


flag = os.O_CREAT | os.O_EXCL | os.O_RDWR


def read(sel: selectors.DefaultSelector, fd, end_tag):
    sel.register(fd, selectors.EVENT_READ)
    last_raw = b""
    cont = 1
    try:
        while cont:
            events = sel.select(3)
            # print(f"events: {events}")
            # for key, mask in events:
            try:
                raw = os.read(fd, 100)
                # print(raw)
                if raw == last_raw:
                    print(f"raw is last_raw")
                    cont = 0
                elif raw.endswith(end_tag):
                    cont = 0
                else:
                    last_raw = raw
                # log = msg_unpack(raw)
                # print(log)
                # if log["gtid"] == 100:
                #     break
            except Exception as e:
                print(e)
    finally:
        sel.unregister(fd)


async def aread(fd, end_tag):
    sel = selectors.DefaultSelector()
    loop = asyncio.get_running_loop()

    waitt: Optional[asyncio.Future] = None
    def _read():
        nonlocal waitt
        waitt = loop.create_future()
        d = os.read(fd, 100)
        waitt.set_result(d)

    # loop.add_reader(fd, _read)
    sel.register(fd, selectors.EVENT_READ)
    try:
        last_raw = b""
        cont = 1
        while cont:
            # if waitt:
            #     print(f"read data")
            #     raw = await asyncio.wait_for(waitt, 1)
            #     print(raw)
            #     if raw == last_raw:
            #         print(f"raw is last_raw")
            #         cont = 0
            #     elif raw.endswith(end_tag):
            #         print(f"stream end")
            #         cont = 0
            #     else:
            #         last_raw = raw
            # await asyncio.sleep(0)
            events = sel.select(1)
            for key, mask in events:
                if mask == selectors.EVENT_READ:
                    raw = os.read(fd, 100)
                    print(raw)
                    if raw == last_raw:
                        print("raw is last_raw")
                        cont = 0
                    elif raw.endswith(end_tag):
                        print("stream end")
                        cont = 0
                    else:
                        last_raw = raw
    except Exception as e:
        print(e)
    finally:
        sel.unregister(fd)
        # loop.remove_reader(fd)


def aread_call(fd, end_tag):
    try:
        raw = os.read(fd, 100)
        print(raw)
        if raw.endswith(end_tag):
            print(f"read end.")
            return
    except Exception as e:
        print(e)


def write(fd, end_tag):
    sel = selectors.DefaultSelector()
    sel.register(fd, selectors.EVENT_WRITE)
    i = 0
    while i <= 100:
        events = sel.select(1)
        for key, mask in events:
            if key.fileobj == fd:
                log = {
                    "gtid": (i := i + 1),
                    "action": "update",
                    "key": "tttxxxhhh",
                    "value": {
                        "name": "hostname",
                        "ip": "1.1.1.1",
                        "stat": "running" if i % 2 else "stop",
                        "remote_hosts": ["hostname1", "hostname2", "hostname3"]
                    }
                }
                os.write(fd, msg_pack(log))
    os.write(fd, end_tag)
    print("write end.")


def test():
    r, w = os.pipe()
    print(r, type(r))
    print(w, type(w))
    end_tag = to_bytes("HugeDataEnd")
    sel = selectors.DefaultSelector()
    with ProcessPoolExecutor() as pool:
        fu = pool.submit(write, w, end_tag)
        read(sel, r, end_tag)
    os.close(w)
    os.close(r)


async def atest():
    print(f"event loop policy: {asyncio.get_event_loop_policy()}")
    loop = asyncio.get_running_loop()
    print(f"loop type: {type(loop)}")
    r, w = os.pipe()
    end_tag = to_bytes("HugeDataEnd")
    executor = ProcessPoolExecutor()
    fu = run_in_executor(loop, executor, write, w, end_tag)
    # loop.add_reader(r, aread_call, r, end_tag)
    await aread(r, end_tag)
    # await asyncio.sleep(1)
    await fu
    os.close(r)
    os.close(w)
    # await t
    # if t.exception():
    #     raise t.exception()


if __name__ == '__main__':
    # test()
    asyncio.set_event_loop_policy(UnixEPollEventLoopPolicy())
    asyncio.run(atest())
