# -*- coding: utf-8 -*-
# Author      : ShiFan
# Created Date: 2024/3/1 9:21
import asyncio
import sys
import time

import zmq.constants as z_const
import zmq.asyncio as z_aio
from gaterpc.core import Context


async def test_req(name: str, route_addr: str, ctx=None):
    if not ctx:
        ctx = Context()
    socket = ctx.socket(z_const.REQ, z_aio.Socket)
    socket.set(z_const.IDENTITY, name.encode("utf-8"))
    socket.set_hwm(3000)
    socket.set(z_const.CONNECT_TIMEOUT, 3000)
    socket.set(z_const.SNDTIMEO, 3000)
    socket.set(z_const.RCVTIMEO, 3000)
    print("connect timeout", socket.get(z_const.CONNECT_TIMEOUT))
    print("recv timeout", socket.get(z_const.RCVTIMEO))
    print("send timeout", socket.get(z_const.SNDTIMEO))
    print("heartbeat timeout", socket.get(z_const.HEARTBEAT_TIMEOUT))
    try:
        print(time.time())
        socket.connect(route_addr)
        print(time.time())
        for i in range(10):
            req = [b"test req", str(i).encode("utf-8")]
            print(time.time())
            await socket.send_multipart(req)
            print(time.time())
            replies = await socket.recv_multipart()
            print(time.time())
            print(replies)
    finally:
        print(time.time())


if __name__ == '__main__':
    argv = sys.argv[1:]
    name = argv[0]
    route_addr = argv[1]
    asyncio.run(test_req(name, route_addr))
