from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any

def _setup_master_tools(mcp: FastMCP, controller) -> None:
    """Setup master track-related MCP tools."""

    @mcp.tool("get_master_track")
    def get_master_track(ctx: Context) -> Dict[str, Any]:
        """Get information about the master track."""
        try:
            info = controller.get_master_track()
            return {"status": "success", "message": f"Master track info: {info}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get master track info: {str(e)}"}

    @mcp.tool("set_master_volume")
    def set_master_volume(ctx: Context, volume: float) -> Dict[str, Any]:
        """Set the master track volume."""
        try:
            if controller.set_master_volume(volume):
                return {"status": "success", "message": f"Set master volume to {volume}"}
            return {"status": "error", "message": "Failed to set master volume"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to set master volume: {str(e)}"}

    @mcp.tool("set_master_pan")
    def set_master_pan(ctx: Context, pan: float) -> Dict[str, Any]:
        """Set the master track pan."""
        try:
            if controller.set_master_pan(pan):
                return {"status": "success", "message": f"Set master pan to {pan}"}
            return {"status": "error", "message": "Failed to set master pan"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to set master pan: {str(e)}"}

    @mcp.tool("toggle_master_mute")
    def toggle_master_mute(ctx: Context, mute: Optional[bool] = None) -> Dict[str, Any]:
        """Toggle or set the master track mute state."""
        try:
            if controller.toggle_master_mute(mute):
                state = "muted" if mute else "unmuted" if mute is not None else "toggled"
                return {"status": "success", "message": f"Master track {state}"}
            return {"status": "error", "message": "Failed to toggle master mute"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to toggle master mute: {str(e)}"}

    @mcp.tool("toggle_master_solo")
    def toggle_master_solo(ctx: Context, solo: Optional[bool] = None) -> Dict[str, Any]:
        """Toggle or set the master track solo state."""
        try:
            if controller.toggle_master_solo(solo):
                state = "soloed" if solo else "unsoloed" if solo is not None else "toggled"
                return {"status": "success", "message": f"Master track {state}"}
            return {"status": "error", "message": "Failed to toggle master solo"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to toggle master solo: {str(e)}"}

