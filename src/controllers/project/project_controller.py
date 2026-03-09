import reapy
from reapy import reascript_api as RPR
import logging
from typing import Optional, Union
from utils.position_utils import get_time_map_info
from src.controllers.base_controller import BaseController
import os

class ProjectController(BaseController):
    """Controller for project-level operations in Reaper."""
    
    def set_tempo(self, bpm: float) -> bool:
        """
        Set the project tempo.
        
        Args:
            bpm (float): Tempo in beats per minute
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project = reapy.Project()
            project.bpm = float(bpm)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set tempo: {e}")
            return False
    
    def get_tempo(self) -> Optional[float]:
        """
        Get the current project tempo.
        
        Returns:
            float: Current tempo in beats per minute, or None if not available
        """
        try:
            project = reapy.Project()
            return project.bpm
            
        except Exception as e:
            self.logger.error(f"Failed to get tempo: {e}")
            return None

    def get_project_time_signature(self) -> Optional[dict]:
        """Get the default project time signature."""
        try:
            time_map = get_time_map_info()
            if not time_map:
                self.logger.error("Failed to get time map info")
                return None
                
            return {
                "numerator": time_map['time_sig_num'],
                "denominator": time_map['time_sig_den'],
                "bpm": time_map['bpm']
            }
        except Exception as e:
            self.logger.error(f"Failed to get project time signature: {e}")
            return None

    def set_project_time_signature(self, numerator: int, denominator: int) -> bool:
        """Set the default project time signature at project start."""
        try:
            project = reapy.Project()
            return RPR.TimeMap_SetTimeSigAtTime(project.id, 0.0, numerator, denominator)
        except Exception as e:
            self.logger.error(f"Failed to set project time signature: {e}")
            return False

    def set_time_signature(self, numerator: int, denominator: int, position: float) -> bool:
        """Set time signature at specified position. Position can be in seconds or 'measure:beat,fraction' format."""
        try:
            project = reapy.Project()
            return RPR.TimeMap_SetTimeSigAtTime(project.id, position, numerator, denominator)
        except Exception as e:
            self.logger.error(f"Failed to set time signature: {e}")
            return False

    def render_project(self, output_file: str, 
                      start_time: Optional[float] = None,
                      end_time: Optional[float] = None,
                      samplerate: int = 44100,
                      channels: int = 2,
                      **kwargs) -> bool:
        """Render project to file."""
        try:
            project = reapy.Project()
            self.logger.debug(f"Starting render with settings: file={output_file}, sr={samplerate}, ch={channels}")
            
            # Store current time selection
            old_start = project.time_selection.start
            old_end = project.time_selection.end
            
            try:
                # Configure render settings
                output_path = os.path.abspath(output_file)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Set time selection if provided
                if start_time is not None and end_time is not None:
                    project.time_selection = (start_time, end_time)
                    RPR.GetSetProjectInfo(project.id, "RENDER_BOUNDSFLAG", 3, True)  # Use time selection
                else:
                    RPR.GetSetProjectInfo(project.id, "RENDER_BOUNDSFLAG", 0, True)  # Full project
                
                # Configure render settings
                RPR.GetSetProjectInfo(project.id, "RENDER_SETTINGS", 0, True)  # Reset settings
                RPR.GetSetProjectInfo(project.id, "RENDER_CHANNELS", channels, True)
                RPR.GetSetProjectInfo(project.id, "RENDER_SRATE", samplerate, True)
                RPR.GetSetProjectInfo_String(project.id, "RENDER_FILE", output_path, True)
                
                # Apply any additional render settings
                for key, value in kwargs.items():
                    try:
                        RPR.GetSetProjectInfo(project.id, f"RENDER_{key.upper()}", value, True)
                    except Exception as e:
                        self.logger.warning(f"Failed to set render option {key}: {e}")
                
                # Execute render
                reapy.perform_action(41824)  # Render project (simple)
                
                if os.path.exists(output_path):
                    self.logger.debug(f"Render completed: {output_path}")
                    return True
                else:
                    self.logger.error("Render failed - output file not created")
                    return False
                    
            finally:
                # Restore original time selection
                project.time_selection = (old_start, old_end)
                self.logger.debug("Time selection restored")
                    
        except Exception as e:
            self.logger.error(f"Failed to render project: {e}")
            return False
