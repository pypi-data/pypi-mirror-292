import asyncio
from main import Telegraph

graph = Telegraph()

async def main():
    r = await graph.uploadMediaFromFile("test.jpg")

asyncio.run(main())