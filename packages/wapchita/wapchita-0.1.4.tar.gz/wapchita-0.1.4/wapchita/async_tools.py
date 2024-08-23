from typing import Awaitable, Any
import asyncio

async def run_parallel(*funcs: Awaitable[Any]) -> Any:
    return await asyncio.gather(*funcs)
