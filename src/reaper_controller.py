# This file is now just a wrapper around the controllers package

# Import controllers directly from the local directory
from .controllers.base_controller import BaseController
from .controllers.track.track_controller import TrackController
from .controllers.fx.fx_controller import FXController
from .controllers.marker.marker_controller import MarkerController
from .controllers.midi.midi_controller import MIDIController
from .controllers.audio.audio_controller import AudioController
from .controllers.master.master_controller import MasterController
from .controllers.project.project_controller import ProjectController

# Create a combined controller that inherits from all controllers
class ReaperController(
    TrackController,
    FXController,
    MarkerController,
    MIDIController, 
    AudioController,
    MasterController,
    ProjectController,
    BaseController  # BaseController must be last
):
    """Controller for interacting with Reaper using reapy.
    
    This class combines all controller functionality from specialized controllers.
    """
    pass

    @property
    def track(self) -> TrackController:
        """Get the track controller for track operations."""
        return TrackController()

    @property
    def fx(self) -> FXController:
        """Get the FX controller for effects operations."""
        return FXController()

    @property
    def marker(self) -> MarkerController:
        """Get the marker controller for timeline operations."""
        return MarkerController()

    @property
    def midi(self) -> MIDIController:
        """Get the MIDI controller for MIDI operations."""
        return MIDIController()

    @property
    def audio(self) -> AudioController:
        """Get the audio controller for audio item operations."""
        return AudioController()

    @property
    def master(self) -> MasterController:
        """Get the master controller for master track operations."""
        return MasterController()

    @property
    def project(self) -> ProjectController:
        """Get the project controller for project-level operations."""
        return ProjectController()

# Re-export the ReaperController class for backward compatibility
__all__ = ['ReaperController']
