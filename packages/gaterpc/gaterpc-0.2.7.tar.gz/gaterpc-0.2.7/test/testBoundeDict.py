import asyncio

from gaterpc.utils import BoundedDict


async def test():
    d = BoundedDict(1000, 3.0)
    await asyncio.gather(
        test_get(d),
        test_pop(d),
        test_set(d),
    )
    d["aset"] = "test sync set"
    await asyncio.sleep(1)
    print(f"get 'aset': {d.get('aset')}")
    print(f"length: {len(d)}")


async def test_get(d):
    aget1000 = await d.aget(1000, "failed")
    print(f"first time aget '1000': {aget1000}")
    await asyncio.sleep(1)
    aget1000 = await d.aget(1000, "failed")
    print(f"second time aget '1000': {aget1000}")
    await asyncio.sleep(1)
    aset = await d.aget("aset", "failed")
    print(f"first time aget 'aset': {aset}")
    sec_aset = await d.aget("aset", "failed")
    print(f"second time aget 'aset': {sec_aset}")


async def test_pop(d):
    apop1000 = await d.apop(1000, "failed")
    print(f"first time apop '1000': {apop1000}")
    apop1000 = await d.apop(1000, "failed")
    print(f"second time apop '1000': {apop1000}")
    await asyncio.sleep(1)
    print(f"popitem: {d.popitem()}")
    aset = await d.apop("aset", "failed")
    print(f"first time apop 'aset' : {aset}")
    sec_aset = await d.apop("aset", "failed")
    print(f"second time apop 'aset' : {sec_aset}")


async def test_set(d):
    for i in range(1000):
        print(f"aset {i}")
        await d.aset(i, i)
        await asyncio.sleep(0)
    _as = asyncio.create_task(d.aset(1000, "test 1000"))
    _as1 = asyncio.create_task(d.aset(1001, "test 1001"))
    print(f"pop: {d.pop(1)}")
    print(f"pop: {d.pop(2)}")
    await asyncio.sleep(3)
    await d.aset("aset", "first time aset.")
    await asyncio.sleep(1)
    await d.aset("aset", "second time aset.")
    await _as
    await _as1


def main():
    asyncio.run(test())
    print(f"test is callable: {callable(test)}")


if __name__ == '__main__':
    main()
