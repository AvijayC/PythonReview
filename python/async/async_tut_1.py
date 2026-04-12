# Notes:
# Sync code: Subway with 1 worker - 1 customer at a time, sequentially.
# Concurrent code: McDonalds, someone takes your order, moves on to next customer while your food is cooking.
# Asyncio: single threaded, single process. Tasks give up control voluntarily.

import asyncio
import time

def sync_function(test_param: str) -> str:
    print("This is a sync function")
    time.sleep(0.1)
    return f"Sync result: {test_param}"

# async def main():
#     # Simple - just running a sync function inside an async main.
#     sync_result = sync_function("Test")
#     print(sync_result)
    
async def main():
    loop = asyncio.get_running_loop()
    future = loop.create_future()  # Like a JS promimse.
    
    future.set_result("Future Result: Test")
    future_result = await future  # To use await, must be within async function.
    print(future_result)
    
    
if __name__ == "__main__":
    # You cannot call an async function normally. You must run an event loop.
    # This allows for cooperative concurrency (threads can give up control)
    asyncio.run(main())  # Starting event loop, which manages async functions.
    
