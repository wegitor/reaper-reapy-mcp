#!/usr/bin/env python
# Test script to verify the controller structure works correctly

import sys
import os
import logging

# Add the repository root to the Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the ReaperController
from src.reaper_controller import ReaperController

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Print a header
    print("=" * 50)
    print("REAPER CONTROLLER TEST SCRIPT")
    print("=" * 50)
    
    # Create the controller
    logger.info("Creating ReaperController instance...")
    try:
        controller = ReaperController(debug=True)
        logger.info("Controller created successfully")
    except Exception as e:
        logger.error(f"Failed to create controller: {e}")
        return
    
    # Verify connection
    logger.info("Verifying connection to Reaper...")
    if controller.verify_connection():
        logger.info("✓ Connection verified")
    else:
        logger.error("✗ Failed to connect to Reaper")
        return
    
    # Test a method from each controller
    # Track controller
    logger.info("Testing track creation...")
    try:
        track_index = controller.create_track("Test Track")
        logger.info(f"✓ Track created with index {track_index}")
    except Exception as e:
        logger.error(f"✗ Failed to create track: {e}")
    
    # FX controller
    logger.info("Testing FX addition...")
    try:
        fx_index = controller.add_fx(track_index, "ReaEQ")
        logger.info(f"✓ FX added with index {fx_index}")
    except Exception as e:
        logger.error(f"✗ Failed to add FX: {e}")
    
    # Marker controller
    logger.info("Testing marker creation...")
    try:
        marker_id = controller.create_marker(0, "Test Marker")
        logger.info(f"✓ Marker created with ID {marker_id}")
    except Exception as e:
        logger.error(f"✗ Failed to create marker: {e}")
    
    # Master controller
    logger.info("Testing master volume...")
    try:
        controller.set_master_volume(0.8)  # 80% volume
        logger.info("✓ Master volume set")
    except Exception as e:
        logger.error(f"✗ Failed to set master volume: {e}")
    
    print("\nTest completed. Check the log for results.")

if __name__ == "__main__":
    main()
