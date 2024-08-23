import asyncio

def do_task(func):
    async def wrapper(*args, **kwargs):
        asyncio.create_task(func(*args, **kwargs))
    return wrapper