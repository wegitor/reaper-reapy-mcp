import asyncio
import pytest
from mcp_abstraction import mcp_abstraction_parse_tool_list

import os
from sample_audio import ensure_sample_file

async def run_tools():
    sample_audio_path = os.path.abspath(ensure_sample_file())

    # Test sequence for audio tools
    tool_seq_to_call = [
        {
            "name" : "create_track",
            "args" : { "name": "Test Track 1"}
        },
        {
            "name" : "insert_audio_item",
            "args" : {
                "track_index": 0,
                "file_path": sample_audio_path,
                "start_measure": "1:1,000"
            }
        },
        {
            "name" : "get_selected_items",
            "args" : {}
        },
        {
            "name" : "set_item_length",
            "args" : {
                "track_index": 0,
                "item_id" : 0,
                "length_measure": "2:1,000"
            }
        },
        {
            "name": "duplicate_item",
            "args": {
                "track_index": 0,
                "item_id": 0,
                "new_time": 10.0,
                "new_measure": "2:1,000"
            }
        },
        {
            "name": "get_item_properties",
            "args": {
                "track_index": 0,
                "item": 0
            }
        },
        {
            "name": "set_item_position",
            "args": {
                "track_index": 0,
                "item_id": 0,
                "position_time": 5.0,
                "position_measure": "2:1,000"
            }
        },
        {
            "name": "get_items_in_time_range",
            "args": {
                "track_index": 0,
                "start_time": 0.0,
                "end_time": 20.0
            }
        },
        {
            "name" : "delete_item",
            "args" : {
                "track_index": 0,
                "item" : 0
            }
        },
        {
            "name" : "delete_item",
            "args" : {
                "track_index": 0,
                "item" : 0
            }
        },
    ]
    await mcp_abstraction_parse_tool_list(tool_seq_to_call)


@pytest.mark.asyncio
async def test_mcp_tools_audio():
    """Test audio-related MCP tools."""
    print("Running audio tools test. ..")
    await run_tools()
    print("Audio tools test completed.")

if __name__ == "__main__":
    asyncio.run(run_tools())
