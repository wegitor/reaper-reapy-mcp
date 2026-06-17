import asyncio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import Dict, Any
import json

async def run_tool_wrap(session: any, name: str, args: Dict[str, Any]):
    print(f"Run tool: {name}")
    result = await session.call_tool(name, args)
    for content in result.content:
        if isinstance(content, types.TextContent):
            print(f"Text: {content.text}")
            data = json.loads(content.text)
            assert data["status"] == "success"

async def parse_tool_results():
    """Demonstrates how to parse different types of content in CallToolResult."""
    server_params = StdioServerParameters(
        command="python", args=["-m", "src.reaper_reapy_mcp"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")

            await run_tool_wrap(session, "test_connection", {"format": "text"})
            await run_tool_wrap(session, "get_tempo", {"format": "text"})
            await run_tool_wrap(session, "create_track", {"name": "test track"})
            await run_tool_wrap(session, "create_midi_item", {"track_index": 0,"start_measure": "1:1,0", "length_measure": "1:1,0"})
            await run_tool_wrap(session, "create_track", {"name": "test track"})


async def main():
    await parse_tool_results()


if __name__ == "__main__":
    asyncio.run(main())
