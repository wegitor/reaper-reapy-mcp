from mcp import types
from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any, List, Union
import reapy

from reaper_reapy_mcp.mcp.tools.mcp_tools_track   import _setup_track_tools
from reaper_reapy_mcp.mcp.tools.mcp_tools_fx      import _setup_fx_tools
from reaper_reapy_mcp.mcp.tools.mcp_tools_audio   import _setup_audio_tools
from reaper_reapy_mcp.mcp.tools.mcp_tools_midi    import _setup_midi_tools
from reaper_reapy_mcp.mcp.tools.mcp_tools_marker  import _setup_marker_tools
from reaper_reapy_mcp.mcp.tools.mcp_tools_master  import _setup_master_tools
from reaper_reapy_mcp.mcp.tools.mcp_tools_project import _setup_project_tools

def setup_mcp_tools(mcp: FastMCP, controller) -> None:
    """Setup MCP tools for Reaper control."""

    _setup_track_tools(mcp, controller)
    _setup_project_tools(mcp, controller)
    _setup_fx_tools(mcp, controller)
    _setup_marker_tools(mcp, controller)
    _setup_master_tools(mcp, controller)
    _setup_midi_tools(mcp, controller)
    _setup_audio_tools(mcp, controller)

    @mcp.tool("test_connection")
    def test_connection(ctx: Context) -> Dict[str, Any]:
        """Test connection to Reaper."""
        try:
            if controller.verify_connection():
                return {"status": "success", "message": "Connected to Reaper"}
            return {"status": "error", "message": "Failed to connect to Reaper"}
        except Exception as e:
            return {"status": "error", "message": f"Connection test failed: {str(e)}"}
