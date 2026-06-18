from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any
from reaper_reapy_mcp.utils.position_utils import position_to_time, time_to_measure, get_time_map_info

def _setup_project_tools(mcp: FastMCP, controller) -> None:
    """Setup project-related MCP tools."""

    @mcp.tool("set_tempo")
    def set_tempo(ctx: Context, bpm: float) -> Dict[str, Any]:
        """Set the project tempo."""
        try:
            if controller.set_tempo(bpm):
                return {"status": "success", "message": f"Set tempo to {bpm} BPM"}
            return {"status": "error", "message": "Failed to set tempo"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to set tempo: {str(e)}"}

    @mcp.tool("get_tempo")
    def get_tempo(ctx: Context) -> Dict[str, Any]:
        """Get the current project tempo."""
        try:
            tempo = controller.get_tempo()
            return {"status": "success", "message": f"Current tempo: {tempo} BPM"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get tempo: {str(e)}"}

    @mcp.tool("get_time_signature")
    def get_time_signature(ctx: Context) -> Dict[str, Any]:
        """Get the current time signature of the project."""
        try:
            time_map = get_time_map_info()
            return {
                "status": "success",
                "time_signature": {
                    "numerator": time_map['time_sig_num'],
                    "denominator": time_map['time_sig_den'],
                    "bpm": time_map['bpm']
                }
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to get time signature: {str(e)}"}

    @mcp.tool("set_project_time_signature")
    def set_project_time_signature(ctx: Context, numerator: int, denominator: int) -> Dict[str, Any]:
        """Set the default project time signature.
        
        Args:
            numerator: Time signature numerator (e.g., 4 in 4/4)
            denominator: Time signature denominator (e.g., 4 in 4/4)
        """
        try:
            if controller.set_project_time_signature(numerator, denominator):
                return {
                    "status": "success", 
                    "message": f"Set project time signature to {numerator}/{denominator}",
                    "time_signature": {
                        "numerator": numerator,
                        "denominator": denominator
                    }
                }
            return {"status": "error", "message": "Failed to set project time signature"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to set project time signature: {str(e)}"}

    @mcp.tool("get_project_time_signature")
    def get_project_time_signature(ctx: Context) -> Dict[str, Any]:
        """Get the default project time signature."""
        try:
            time_sig = controller.get_project_time_signature()
            return {
                "status": "success",
                "time_signature": time_sig
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to get project time signature: {str(e)}"}

    @mcp.tool("set_time_signature")
    def set_time_signature(ctx: Context, numerator: int, denominator: int, 
                          position: Optional[str] = None, 
                          time: Optional[float] = None) -> Dict[str, Any]:
        """Set time signature at specified position.
        
        Args:
            numerator: Time signature numerator (e.g., 4 in 4/4)
            denominator: Time signature denominator (e.g., 4 in 4/4)
            position: Position as "measure:beat,fraction" (optional if time is provided)
                     where fraction is milliseconds (e.g., "1:1,500" = measure 1, beat 1, half beat)
            time: Position in seconds (optional if position is provided)
        """
        try:
            # Determine position
            if position is not None:
                pos = position_to_time(position)
                measure_pos = position
            elif time is not None:
                pos = float(time)
                measure_pos = time_to_measure(pos)
            else:
                pos = 0.0
                measure_pos = "1:1.000"
                
            if controller.set_time_signature(numerator, denominator, pos):
                return {
                    "status": "success", 
                    "message": f"Set time signature to {numerator}/{denominator} at position {measure_pos}",
                    "position": {"time": pos, "measure": measure_pos}
                }
            return {"status": "error", "message": "Failed to set time signature"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to set time signature: {str(e)}"}

    @mcp.tool("render_project")
    def render_project(ctx: Context, 
                      output_file: str,
                      start_time: Optional[float] = None,
                      end_time: Optional[float] = None,
                      start_measure: Optional[str] = None,
                      end_measure: Optional[str] = None,
                      samplerate: int = 44100,
                      channels: int = 2,
                      file_format: str = "wave") -> Dict[str, Any]:
        """Render project to audio file.
        
        Args:
            output_file: Path to output audio file
            start_time: Start position in seconds (optional if start_measure is provided)
            end_time: End position in seconds (optional if end_measure is provided)
            start_measure: Start position as "measure:beat,fraction" (optional if start_time is provided)
            end_measure: End position as "measure:beat,fraction" (optional if end_time is provided)
            samplerate: Sample rate in Hz (default: 44100)
            channels: Number of channels (default: 2)
            file_format: Formats available on this machine
                "wave" "aiff" "iso " "ddp "
                "flac" "mp3l" "oggv" "OggS"
                "FFMP" "GIF " "LCF " "wvpk"
        """
        try:
            # Convert measure positions to time if provided
            render_start = None
            render_end = None
            
            if start_time is not None:
                render_start = float(start_time)
                start_pos = time_to_measure(render_start)
            elif start_measure is not None:
                render_start = position_to_time(start_measure)
                start_pos = start_measure
                
            if end_time is not None:
                render_end = float(end_time)
                end_pos = time_to_measure(render_end)
            elif end_measure is not None:
                render_end = position_to_time(end_measure)
                end_pos = end_measure
            
            # Perform render
            if controller.render_project(output_file, file_format, render_start, render_end, 
                                      samplerate, channels):
                response = {
                    "status": "success",
                    "message": f"Project rendered to {output_file}",
                    "file": output_file,
                    "settings": {
                        "samplerate": samplerate,
                        "channels": channels
                    }
                }
                
                # Add time range info if provided
                if render_start is not None or render_end is not None:
                    response["range"] = {
                        "start": {"time": render_start, "measure": start_pos} if render_start is not None else None,
                        "end": {"time": render_end, "measure": end_pos} if render_end is not None else None
                    }
                    
                return response
            return {"status": "error", "message": "Failed to render project"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to render project: {str(e)}"}

