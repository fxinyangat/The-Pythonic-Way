# ASYNC GENERATORS

"""A regular generaroe yields values that are immediately ready.
But if producing each value requires waiting on I/O - e.g fetching page from API, reading files from 
a network, a normal generator would block the entire event loop while waiting
Aync Generator combines aync/await with yield: it can await slow operations between yields, letting other
coroutines run during the await.
"""

# Basic Syntax
import asyncio, time

async def fetch_account(account_id:str) -> dict:
    await asyncio.sleep(1)
    
    return {"id": account_id, "balance": 1000}


async def sequential():
    start = time.perf_counter()
    a = await fetch_account("ACC001")
    b = await fetch_account("ACC002")
    c = await fetch_account("ACC003")
    
    # print(f"Sequential: {time.perf_counter() - start:.1f}s")
    
    
    
async def concurrent():
    start = time.perf_counter()
    results = await asyncio.gather(
        fetch_account("ACC001"),
        fetch_account("ACC002"),
        fetch_account("ACC003")
        
    )
    # print(f"Concurrent: {time.perf_counter() - start:.1f}s")
    # print(results)
    
# Gathering a dynamic list

async def fetch_all(account_ids: list[str]) -> list[dict] | None:
    tasks = [fetch_account(aid) for aid in account_ids]
    start = time.perf_counter()
    results = await asyncio.gather(*tasks)
    # print(f"Fetchall: {time.perf_counter() - start:.1f}s")
    # print(results)
    
    


    
asyncio.run(sequential())
asyncio.run(concurrent())

asyncio.run(fetch_all(["ACC001","ACC002","ACC003","ACC004"]))


#TASK GROUP
async def main():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fetch_account("ACC001"))
        t2 = tg.create_task(fetch_account("ACC002"))
    # block has exited → all tasks done → safe to read results
    # print(t1.result())   # {'id': 'ACC001', 'balance': 1000}
    # print(t2.result())
    
    
asyncio.run(main())

"""gather vs TaskGroup — which to use
Use TaskGroup by default on Python 3.11+. It's the structured-concurrency approach: failures cancel siblings, 
nothing leaks, cleanup is guaranteed. It's what you want when the tasks form a logical unit and one 
failing means the rest are pointless.
Use gather when you specifically want the return_exceptions=True behaviour — every task runs to 
completion independently, and you handle each result or failure individually. It's also still the tool 
on Python versions before 3.11."""

#   QUEUE   

import asyncio
import random

async def producer(queue, count):
    # Generate work items to put in the queue
    
    for i in range(1,count + 1):
        item = f"Task-{i}"
        
        print(f"Producer created {item}")
        
        await queue.put(item)
        await asyncio.sleep(random.uniform(0.1,0.3))
        
        
async def consumer(name, queue):
    
    # Retrieve items from queue and process them
    
    while True:
        item = await queue.get()
        try:
            print(f"Consumer {name} processing {item}")
            
            await asyncio.sleep(random.uniform(0.1,0.3))
            print(f"Consumer {name}: Finished {item}")
            
        finally:
            # Always signal completion even if the exception occurs
            queue.task_done()

async def main():
    # Initialize a queue with a limit of 5 items to prevent unbounded memory usage
    queue = asyncio.Queue(maxsize=5)
    
    # 1. Start the consumers as background tasks
    # They run indefinitely in an infinite loop
    consumers = [
        asyncio.create_task(consumer(f"Worker-{i}", queue))
        for i in range(3)  # Spin up 3 concurrent workers
    ]
    
    # 2. Start the producer and wait for it to finish adding items
    await producer(queue, 10)
    
    # 3. Wait until all items in the queue are fully processed
    await queue.join()
    
    # 4. Clean up: Cancel the consumer tasks since they are in infinite loops
    for c in consumers:
        c.cancel()
        
    # Wait for cancellation status to finalize across consumers
    await asyncio.gather(*consumers, return_exceptions=True)
    print("All work complete. System shut down.")

if __name__ == "__main__":
    asyncio.run(main())

