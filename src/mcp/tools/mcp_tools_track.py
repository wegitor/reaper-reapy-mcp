
from mcp import types
from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any, List, Union
import reapy

def _setup_track_tools(mcp: FastMCP, controller) -> None:
    """Setup track-related MCP tools."""

    @mcp.tool("create_track")
    def create_track(ctx: Context, name: Optional[str] = None) -> Dict[str, Any]:
        """Note: Track indices in REAPER API are 0-based (first track = 0, second = 1, etc.)
              However, REAPER's visual interface displays tracks starting from 1.
              So track 0 in API = Track 1 in REAPER UI.
        """
        try:
            track_index = controller.create_track(name)
            return {"status": "success", "message": f"Created track {track_index}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to create track: {str(e)}"}

    @mcp.tool("rename_track")
    def rename_track(ctx: Context, track_index: int, new_name: str) -> Dict[str, Any]:
        """Rename an existing track.
        
        Args:
            track_index: 0-based track index (0 = first track, 1 = second, etc.)
                        Note: REAPER UI shows tracks starting from 1, but API uses 0-based indexing.
                        API track 0 = UI Track 1, API track 1 = UI Track 2, etc.
            new_name: New name for the track
        """
        try:
            if controller.rename_track(track_index, new_name):
                return {"status": "success", "message": f"Renamed track {track_index} to {new_name}"}
            return {"status": "error", "message": f"Failed to rename track {track_index}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to rename track: {str(e)}"}

    @mcp.tool("set_track_color")
    def set_track_color(ctx: Context, track_index: int, color: str) -> Dict[str, Any]:
        """Set the color of a track.
        
        Args:
            track_index: 0-based track index (0 = first track, 1 = second track, etc.)
            color: Color value
        """
        try:
            if controller.set_track_color(track_index, color):
                return {"status": "success", "message": f"Set color of track {track_index} to {color}"}
            return {"status": "error", "message": f"Failed to set color for track {track_index}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to set track color: {str(e)}"}

    @mcp.tool("get_track_color")
    def get_track_color(ctx: Context, track_index: int) -> Dict[str, Any]:
        """Get the color of a track.
        
        Args:
            track_index: 0-based track index (0 = first track, 1 = second track, etc.)
        """
        try:
            color = controller.get_track_color(track_index)
            return {"status": "success", "message": f"Color of track {track_index}: {color}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get track color: {str(e)}"}

    @mcp.tool("get_track_count")
    def get_track_count(ctx: Context) -> Dict[str, Any]:
        """Get the number of tracks in the project."""
        try:
            count = controller.get_track_count()
            return {"status": "success", "track_count": count}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get track count: {str(e)}"}
            
    @mcp.tool("get_track_list")
    def get_track_list(ctx: Context) -> Dict[str, Any]:
        """Get a list of all tracks in the project.

        Returns:
            Dict containing status and a list of tracks, each with:
            - index: Track index
            - name: Track name
            - color: Track color (if available)
        """
        try:
            tracks = []
            project = reapy.Project()
            for i, track in enumerate(project.tracks):
                track_info = {
                    "index": i,
                    "name": track.name,
                    "color": getattr(track, "color", None)
                }
                tracks.append(track_info)
            return {
                "status": "success",
                "tracks": tracks,
                "count": len(tracks)
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to get track list: {str(e)}"}


