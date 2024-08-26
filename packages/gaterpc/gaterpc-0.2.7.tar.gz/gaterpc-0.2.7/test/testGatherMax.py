# -*- coding: utf-8 -*-
# Author      : ShiFan
# Created Date: 2024/8/12 下午5:44
import asyncio


async def simple_task(id):
    await asyncio.sleep(1)
    return f"Task {id} completed"


async def main():
    tasks = []
    try:
        # 修改这个数字，来测试系统对大量任务的处理能力
        num_tasks = 100000

        for i in range(num_tasks):
            task = asyncio.create_task(simple_task(i))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        print(f'Completed {len(results)} tasks')

    except Exception as e:
        print(f'An exception occurred: {e}')

if __name__ == "__main__":
    asyncio.run(main())
