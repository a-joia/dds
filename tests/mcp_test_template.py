import asyncio
from fastmcp import Client
import json

client = Client("http://127.0.0.1:8088/mcp")


async def main():
    async with client:

        result = client.call_tool("<tool function name>",{"arg1":"value"})

asyncio.run(main())