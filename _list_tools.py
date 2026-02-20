import asyncio, json
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def main():
    async with streamablehttp_client("https://cnx-demo-mcp-server-wmck.onrender.com/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            for t in tools.tools:
                print(f"Tool: {t.name}")
                print(f"  Description: {t.description}")
                print(f"  Parameters: {json.dumps(t.inputSchema, indent=4)}")
                print()

asyncio.run(main())
