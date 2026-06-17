import reapy
import logging
from typing import Optional

from ..base_controller import BaseController

class TrackController(BaseController):
    """Controller for track-related operations in Reaper."""
    
    def create_track(self, name: Optional[str] = None) -> int:
        """
        Create a new track in Reaper.
        
        Args:
            name (str, optional): Name for the new track
            
        Returns:
            int: Index of the created track
        """
        try:
            project = reapy.Project()
            # Get current track count to determine where the new track will be added
            current_track_count = len(project.tracks)
            self.logger.info(f"Current track count: {current_track_count}")
            
            # Add track at the end (after all existing tracks)
            track = project.add_track(index=current_track_count, name=name or "")
            
            # Get the final track count and the actual index
            final_track_count = len(project.tracks)
            actual_index = final_track_count - 1  # Last track index
            
            self.logger.info(f"Added track. Final track count: {final_track_count}, returning index: {actual_index}")
            return actual_index

        except Exception as e:
            self.logger.error(f"Failed to create track: {e}")
            raise

    def rename_track(self, track_index: int, new_name: str) -> bool:
        """
        Rename an existing track.
        
        Args:
            track_index (int): Index of the track to rename
            new_name (str): New name for the track
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project = reapy.Project()
            track = project.tracks[track_index]
            track.name = new_name
            return True

        except Exception as e:
            self.logger.error(f"Failed to rename track: {e}")
            return False

    def get_track_count(self) -> int:
        """Get the number of tracks in the project."""
        try:
            project = reapy.Project()
            return len(project.tracks)

        except Exception as e:
            self.logger.error(f"Failed to get track count: {e}")
            return 0
            
    def set_track_color(self, track_index: int, color: str) -> bool:
        """
        Set the color of a track.
        
        Args:
            track_index (int): Index of the track
            color (str): Hex color code (e.g., "#FF0000")
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project = reapy.Project()
            track = project.tracks[track_index]
            # Convert hex color to RGB
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            track.color = (r, g, b)
            return True

        except Exception as e:
            self.logger.error(f"Failed to set track color: {e}")
            return False

    def get_track_color(self, track_index: int) -> str:
        """Get the color of a track."""
        try:
            project = reapy.Project()
            track = project.tracks[track_index]
            r, g, b = track.color
            # Return uppercase hex color to match expected format in tests
            return f"#{r:02X}{g:02X}{b:02X}"
            
        except Exception as e:
            self.logger.error(f"Failed to get track color: {e}")
            return "#000000"
