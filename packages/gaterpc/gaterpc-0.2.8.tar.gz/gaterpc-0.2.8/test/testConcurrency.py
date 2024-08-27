# -*- coding: utf-8 -*-
# Author      : ShiFan
# Created Date: 2024/2/5 15:45
import asyncio
# import uvloop
import time
import concurrent.futures


async def test():
    from gaterpc.core import Client
    from gaterpc.global_settings import Settings

    # Settings.EVENT_LOOP_POLICY = uvloop.EventLoopPolicy()
    Settings.DEBUG = True
    Settings.setup()
    loop = asyncio.get_event_loop()
    loop.slow_callback_duration = 0.01
    gr_cli = Client(
        broker_addr="tcp://127.0.0.1:777",
        # zap_mechanism=Settings.ZAP_MECHANISM_PLAIN.decode("utf-8"),
        # zap_credentials=(
        #     Settings.ZAP_PLAIN_DEFAULT_USER,
        #     Settings.ZAP_PLAIN_DEFAULT_PASSWORD
        # )
    )
    # await asyncio.sleep(2)
    start = time.time()
    ts = [
        loop.create_task(gr_cli.Gate.query_service("GateRPC"))
        for i in range(2000)
    ]
    for t in ts:
        await t
    end = time.time()
    gr_cli.close()
    return end - start


def test_thread():
    use_time = asyncio.run(test())
    if use_time > 1:
        print(use_time)


def main():
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     fs = []
    #     start = time.time()
    #     for i in range(1000):
    #         print(f"{i}", end="\r")
    #         f = executor.submit(test_thread)
    #         fs.append(f)
    #     concurrent.futures.wait(fs, 60)
    #     end = time.time()
    #     print(f"Total time: {end - start}")
    test_thread()


if __name__ == '__main__':
    main()
