import asyncio
import pytest
from mcp_abstraction import mcp_abstraction_parse_tool_list

async def run_tools():
    tool_seq_to_call = [
        {
            "name" : "create_track",
            "args" : {
                "name": "Test Track 1"
            }
        },
        {
            "name" : "create_track",
            "args" : {
                "name": "Test Track 2"
            }
        },
        {
            "name" : "get_track_count", "args" : {}
        },
        {
            "name" : "get_track_list", "args" : {}
        },
        {
            "name" : "rename_track",
            "args" : {
                "track_index": 0,
                "new_name": "Renamed Track 1"
            }
        },
        {
            "name" : "set_track_color",
            "args" : {
                "track_index": 0,
                "color": "#FF0000"
            }
        },
        {
            "name" : "get_track_color",
            "args" : {
                "track_index": 0
            }
        }
    ]
    await mcp_abstraction_parse_tool_list(tool_seq_to_call)


@pytest.mark.asyncio
async def test_mcp_tools_track():
    """Test track-related MCP tools."""
    print("Running track tools test. ..")
    await run_tools()
    print("Track tools test completed.")


if __name__ == "__main__":
    asyncio.run(run_tools())
