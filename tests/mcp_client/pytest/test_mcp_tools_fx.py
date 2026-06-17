import asyncio
import pytest
from mcp_abstraction import mcp_abstraction_parse_tool_list

async def run_tools():
    # Test sequence for FX tools
    tool_seq_to_call = [
        {
            "name" : "create_track",
            "args" : { "name": "Test Track 1"}
        },
        {
            "name": "get_available_fx_list",
            "args": {}
        },
        {
            "name": "get_fx_list",
            "args": {
                "track_index": 0
            }
        },
        {
            "name": "add_fx",
            "args": {
                "track_index": 0,
                "fx_name": "ReaEQ (Cockos)"
            }
        },
        {
            "name": "get_fx_list",
            "args": {
                "track_index": 0
            }
        },
        {
            "name": "get_fx_param_list",
            "args": {
                "track_index": 0,
                "fx_index": 0
            }
        },
        {
            "name": "set_fx_param",
            "args": {
                "track_index": 0,
                "fx_index": 0,
                "param_name": "Global Gain",
                "value": 0.5
            }
        },
        {
            "name": "get_fx_param",
            "args": {
                "track_index": 0,
                "fx_index": 0,
                "param_name": "Global Gain"
            }
        },
        {
            "name": "toggle_fx",
            "args": {
                "track_index": 0,
                "fx_index": 0,
                "enable": True
            }
        },
        {
            "name": "remove_fx",
            "args": {
                "track_index": 0,
                "fx_index": 0
            }
        }
    ]
    await mcp_abstraction_parse_tool_list(tool_seq_to_call)

@pytest.mark.asyncio
async def test_mcp_tools_fx():
    """Test FX-related MCP tools."""
    print("Running FX tools test. ..")
    await run_tools()
    print("FX tools test completed.")

if __name__ == "__main__":
    asyncio.run(run_tools())
