import reapy
import logging
from typing import Dict, Any

from ..base_controller import BaseController

class MarkerController(BaseController):
    """Controller for marker and region-related operations in Reaper."""
    
    def create_region(self, start_time: float, end_time: float, name: str) -> int:
        """
        Create a region in the project.
        
        Args:
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            name (str): Name of the region
            
        Returns:
            int: Index of the created region
        """
        try:
            project = reapy.Project()
            region = project.add_region(start_time, end_time, name)
            return region.index
        except Exception as e:
            self.logger.error(f"Failed to create region: {e}")
            return -1

    def delete_region(self, region_index: int) -> bool:
        """
        Delete a region from the project.
        
        Args:
            region_index (int): Index of the region to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:                
            project = reapy.Project()
            
            # Log all region indices for debugging
            region_indices = [r.index for r in project.regions]
            self.logger.debug(f"Available region indices: {region_indices}")
            self.logger.debug(f"Attempting to delete region with index: {region_index}")
            
            # Try to find the region by index - first with exact match
            for region in project.regions:
                if region.index == region_index:
                    region.delete()
                    self.logger.info(f"Deleted region with index {region_index}")
                    return True
            
            # If not found, try with string comparison
            str_region_index = str(region_index)
            for region in project.regions:
                if str(region.index) == str_region_index:
                    region.delete()
                    self.logger.info(f"Deleted region with string index match {region_index}")
                    return True
            
            # If still not found, use ReaScript API directly
            try:
                # Try to delete using ReaScript API
                from reapy import reascript_api as RPR
                result = RPR.DeleteProjectMarker(0, region_index, True)  # isRegion=True
                if result:
                    self.logger.info(f"Deleted region using ReaScript API {region_index}")
                    return True
            except Exception as e:
                self.logger.warning(f"Failed to delete region with ReaScript API: {e}")
                
            # As a fallback, try the project's method
            try:
                # Try to delete by index directly
                project.delete_region_by_index(region_index)
                self.logger.info(f"Deleted region using delete_region_by_index {region_index}")
                return True
            except Exception as e:
                self.logger.warning(f"Failed to delete region with delete_region_by_index: {e}")
            
            self.logger.error(f"Could not find region with index {region_index}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete region: {e}")
            return False

    def create_marker(self, time: float, name: str) -> int:
        """
        Create a marker in the project.
        
        Args:
            time (float): Time position in seconds
            name (str): Name of the marker
            
        Returns:
            int: Index of the created marker
        """
        try:
            project = reapy.Project()
            marker = project.add_marker(time, name)
            return marker.index
        except Exception as e:
            self.logger.error(f"Failed to create marker: {e}")
            return -1

    def delete_marker(self, marker_index: int) -> bool:
        """
        Delete a marker from the project.
        
        Args:
            marker_index (int): Index of the marker to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try: 
            project = reapy.Project()
            
            # Log all marker indices for debugging
            marker_indices = [m.index for m in project.markers]
            self.logger.debug(f"Available marker indices: {marker_indices}")
            self.logger.debug(f"Attempting to delete marker with index: {marker_index}")
            
            # First try direct access with safer index checking
            try:
                markers_list = list(project.markers)
                if markers_list and 0 <= marker_index < len(markers_list):
                    marker = markers_list[marker_index]
                    marker.delete()
                    self.logger.info(f"Deleted marker with direct access: {marker_index}")
                    return True
            except Exception as e:
                self.logger.warning(f"Could not delete marker with direct access: {e}")
            
            # If direct access fails, try to find by index property
            for marker in project.markers:
                if marker.index == marker_index:
                    marker.delete()
                    self.logger.info(f"Deleted marker with index matching: {marker_index}")
                    return True
            
            # Try string comparison
            str_marker_index = str(marker_index)
            for marker in project.markers:
                if str(marker.index) == str_marker_index:
                    marker.delete()
                    self.logger.info(f"Deleted marker with string index matching: {marker_index}")
                    return True
            
            self.logger.error(f"Could not find marker with index {marker_index}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete marker: {e}")
            return False