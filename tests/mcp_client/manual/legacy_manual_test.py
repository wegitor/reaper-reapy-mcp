import asyncio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import Dict, Any
import json
import subprocess
import time
from mcp.client.streamable_http import streamable_http_client
import argparse

async def run_tool_wrap(session: any, name: str, args: Dict[str, Any]):
    print(f"Run tool: {name}")
    result = await session.call_tool(name, args)
    for content in result.content:
        if isinstance(content, types.TextContent):
            print(f"Text: {content.text}")
            data = json.loads(content.text)
            assert data["status"] == "success"

async def run_tools(read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        tools = await session.list_tools()
        print(f"Available tools: {[tool.name for tool in tools.tools]}")

        await run_tool_wrap(session, "test_connection", {"format": "text"})
        await run_tool_wrap(session, "get_tempo", {"format": "text"})
        await run_tool_wrap(session, "create_track", {"name": "test track"})
        await run_tool_wrap(session, "create_midi_item", {"track_index": 0,"start_measure": "1:1,0", "length_measure": "1:1,0"})
        await run_tool_wrap(session, "create_track", {"name": "test track"})

async def parse_tool_results():
    """Demonstrates how to parse different types of content in CallToolResult."""

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--mode", type=str, help="test mode stdio or http", default="std")
    args = parser.parse_args()

    if args.mode == "std":
        server_params = StdioServerParameters(
            command="python", args=["-m", "reaper_reapy_mcp"]
        )
        async with stdio_client(server_params) as (read, write):
            await run_tools(read, write)

    elif args.mode == "http":

        process = subprocess.Popen(["python", "-m", "reaper_reapy_mcp", "--mode", "http"])
        time.sleep(2)

        async with streamable_http_client("http://localhost:3957/mcp") as (
            read,
            write,
            _,
        ):
            await run_tools(read, write)

        process.terminate()    
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


async def main():
    await parse_tool_results()

if __name__ == "__main__":
    asyncio.run(main())
