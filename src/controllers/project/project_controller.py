import reapy
from reapy import reascript_api as RPR
import logging
from typing import Optional, Union
from reaper_reapy_mcp.utils.position_utils import get_time_map_info
from ..base_controller import BaseController
import os
from ..reapy_actions import reapy_actions_enum

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
            cur_tempo = self.get_tempo()
            self.logger.info(f"tempo before time signature set : {cur_tempo}")
            for_ret = RPR.SetTempoTimeSigMarker(project.id, -1, 0.0, 0, 0, cur_tempo, numerator, denominator, False)
            RPR.DeleteTempoTimeSigMarker(project.id, 0)
            return for_ret
        except Exception as e:
            self.logger.error(f"Failed to set project time signature: {e}")
            return False

    def set_time_signature(self, numerator: int, denominator: int, position: float) -> bool:
        """Set time signature at specified position. Position can be in seconds or 'measure:beat,fraction' format."""
        try:
            project = reapy.Project()
            return RPR.SetTempoTimeSigMarker(project.id, -1, position, 0, 0, self.get_tempo(), numerator, denominator, False)
        except Exception as e:
            self.logger.error(f"Failed to set time signature: {e}")
            return False

    def render_project(self, output_file: str,
                       file_format: str = "wave", 
                       start_time: Optional[float] = None,
                       end_time: Optional[float] = None,
                       samplerate: int = 44100,
                       channels: int = 2) -> bool:
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
                self.logger.debug(f"output_path: {output_path}")
                output_name_with_ext = os.path.basename(output_path).split('/')[-1]
                os.makedirs(output_path.split(output_name_with_ext)[0], exist_ok = True)

                outputfile_extension = output_name_with_ext.split('.')[-1]
                outputfile_name = output_name_with_ext.split('.' + outputfile_extension)[0]
                only_path = output_path.split(output_name_with_ext)[0]
                
                # Configure render settings
                project.set_info_value("RENDER_SETTINGS", 0) # RENDER_SETTINGS

                # Set time selection if provided
                if start_time is not None and end_time is not None:
                    project.time_selection = (start_time, end_time)
                    project.set_info_value("RENDER_BOUNDSFLAG", 2)  # Use time selection
                else:
                    project.set_info_value("RENDER_BOUNDSFLAG", 1)  # Full project

                RPR.GetSetProjectInfo(project.id, "RENDER_CHANNELS", channels, True)
                RPR.GetSetProjectInfo(project.id, "RENDER_SRATE", samplerate, True)
                
                project.set_info_string("RENDER_FILE", only_path)
                project.set_info_string("RENDER_PATTERN", outputfile_name)


                supp_formats = ["wave", "aiff", "iso ", "ddp ", "flac", "mp3l", "oggv", "OggS",
                                "FFMP", "GIF ", "LCF ", "wvpk"]
                # Validate input format against formats available on this machine
                if file_format not in supp_formats :
                    self.logger.error("Render failed - unsupported format")
                    return False

                project.set_info_string("RENDER_FORMAT", file_format[::-1])
                project.set_info_string("RENDER_FORMAT2", file_format[::-1])

                reapy.perform_action(int(reapy_actions_enum.RENDER_PROJECT))
                return True

            finally:
                # Restore original time selection
                project.time_selection = (old_start, old_end)
                self.logger.debug("Time selection restored")
                    
        except Exception as e:
            self.logger.error(f"Failed to render project: {e}")
            return False
