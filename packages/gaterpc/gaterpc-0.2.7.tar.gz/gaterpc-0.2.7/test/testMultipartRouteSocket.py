# -*- coding: utf-8 -*-
# Author      : ShiFan
# Created Date: 2024/2/2 17:14
import asyncio
import concurrent
import os
import socket as BaseSocket
import sys
import time
from hashlib import pbkdf2_hmac
from concurrent.futures import ThreadPoolExecutor

import zmq.constants as z_const
import zmq.asyncio as z_aio
from gaterpc.core import Context
from gaterpc.utils import to_bytes


C_KEY = b"Tm"


async def test_socket(
    name: str, addr: str, ctx=None, poller=None, other_addr: list[str] =
    None
):
    nid = pbkdf2_hmac("sha256", to_bytes(addr), C_KEY, 10000)
    print(f"nid: {nid}({type(nid)})")
    if not ctx:
        ctx = Context()
    if not poller:
        poller = z_aio.Poller()
    if not other_addr:
        other_addr = []
    socket = ctx.socket(z_const.ROUTER, z_aio.Socket)
    socket.set(z_const.IDENTITY, nid)
    socket.set_hwm(3000)
    socket.bind(addr)
    poller.register(socket, z_const.POLLIN)
    # 必须先让出线程去执行注册 socket
    nids = {

        _addr: pbkdf2_hmac("sha256", to_bytes(_addr), C_KEY, 10000)
        for _addr in other_addr
    }
    await asyncio.sleep(5)
    for _addr, _nid in nids.items():
        socket.connect(_addr)
        await asyncio.sleep(1)
        hello = [_nid, b"", b"hello"]
        print(f"send hello: {hello}")
        await socket.send_multipart(hello)
    await asyncio.sleep(2)
    # poller = z_aio.Poller()
    i = 10
    ri = 10
    try:
        while i or (ri - 1):
            items = dict(await poller.poll(1000))
            print(f"{name} sockets: {items}")
            if socket in items:
                reply = await socket.recv_multipart()
                print(f"{name} recv multipart: {reply}")
                if reply[-1].decode("utf-8").isdigit():
                    ri = int(reply[-1].decode("utf-8"))
                replies = [*reply, b"name"]
                await socket.send_multipart(replies)
                # if ri - 1:
                #     replies = [reply[0], b"", f"{name}-recv".encode("utf-8"), reply[-1]]
                #     print(f"reply {reply[2]}: {replies}")
                #     await socket.send_multipart(replies)
            if i and nids:
                for _addr, _nid in nids:
                    send_messages = [
                        _nid, b"", f"{name}-send".encode("utf-8"),
                        str(i).encode("utf-8")
                    ]
                    await socket.send_multipart(send_messages)
                    print(f"{name} send to {_addr}: {send_messages}")
                i -= 1
    finally:
        socket.close()
        return


async def atest():
    ctx = Context()
    poller = z_aio.Poller()
    at = asyncio.create_task(test_socket("a", "tcp://127.0.0.1:5555", ctx, poller))
    bt = asyncio.create_task(test_socket("b", "tcp://127.0.0.1:5556", ctx, poller))
    ct = asyncio.create_task(test_socket("c", "tcp://127.0.0.1:5557", ctx, poller))
    await asyncio.sleep(3)
    addrs = [
        "tcp://127.0.0.1:5557", "tcp://127.0.0.1:5556", "tcp://127.0.0.1:5555",
        "tcp://127.0.0.1:6666"
    ]
    for addr in addrs:
        try:
            scan = BaseSocket.socket(BaseSocket.AF_INET, BaseSocket.SOCK_STREAM)
            scan.settimeout(3)
            res = scan.connect_ex(("127.0.0.1", int(addr.split(":")[-1])))
            if res:
                print(f"{addr} connect failed. {res}")
        except Exception as e:
            print(f"{addr} connect failed, {e}")


    socket = ctx.socket(z_const.ROUTER, z_aio.Socket)
    socket.set(z_const.IDENTITY, "route-client-test".encode("utf-8"))
    for _addr in addrs:
        print(f"connect {_addr}")
        print(socket.connect(_addr).addr)
    socket.connect("tcp://127.0.0.1:6666")
    poller.register(socket, z_const.POLLIN)
    _addrs = addrs.copy()
    _addrs.reverse()
    sequence = 0
    while 1:
        for _addr in _addrs:
            print(f"send {_addr}")
            await socket.send_multipart([_addr.encode("utf-8"), b"", f"{sequence}-test".encode("utf-8")])
        items = dict(await poller.poll(1000))
        if socket in items:
            reply = await socket.recv_multipart()
            print(reply)
        sequence += 1


def test(name: str, addr: str, other_addr: list[str]):
    asyncio.run(test_socket(name, addr, None, None, other_addr))


def main():
    asyncio.run(atest())


if __name__ == '__main__':
    argv = sys.argv
    name = argv[1]
    addr = argv[2]
    other_addr = argv[3:]
    print(os.getpid())
    test(name, addr, other_addr)
    # main()
