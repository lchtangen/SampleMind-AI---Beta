"""
DAW Bridge Base Interface

Abstract base class defining the interface for all DAW integrations.
Each DAW plugin implements this interface for consistent functionality.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class DAWType(str, Enum):
    """Supported DAW types"""
    FL_STUDIO = "fl_studio"
    ABLETON = "ableton"
    LOGIC_PRO = "logic_pro"
    GENERIC = "generic"


@dataclass
class DAWProject:
    """Information about the current DAW project"""
    name: str
    path: Optional[str] = None
    tempo: float = 120.0
    key: str = "C"
    time_signature: str = "4/4"
    sample_rate: int = 44100


@dataclass
class DAWChannel:
    """Representation of a mixer channel"""
    index: int
    name: str
    type: str = "audio"  # audio, instrument, aux, master
    volume: float = 1.0
    pan: float = 0.0
    muted: bool = False
    solo: bool = False


class DAWBridge(ABC):
    """
    Abstract base class for DAW integrations.

    Provides a consistent interface for:
    - Connection management
    - Project information
    - Sample management
    - Mixer operations
    """

    @property
    @abstractmethod
    def daw_type(self) -> DAWType:
        """Return the DAW type"""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to DAW"""
        pass

    @abstractmethod
    async def connect(self, host: str = "localhost", port: int = 9000) -> bool:
        """
        Establish connection to DAW.

        Args:
            host: DAW host address
            port: Communication port

        Returns:
            True if connected successfully
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from DAW"""
        pass

    @abstractmethod
    async def get_project_info(self) -> Optional[DAWProject]:
        """
        Get current project information.

        Returns:
            DAWProject with tempo, key, etc.
        """
        pass

    @abstractmethod
    async def get_channels(self) -> List[DAWChannel]:
        """
        Get all mixer channels.

        Returns:
            List of DAWChannel objects
        """
        pass

    @abstractmethod
    async def send_sample(
        self,
        file_path: Path,
        channel: int = 0,
        apply_analysis: bool = True,
    ) -> bool:
        """
        Send a sample to a DAW channel.

        Args:
            file_path: Path to audio file
            channel: Target channel index
            apply_analysis: Auto-adjust tempo/pitch based on analysis

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def set_tempo(self, bpm: float) -> bool:
        """Set project tempo"""
        pass

    @abstractmethod
    async def get_tempo(self) -> float:
        """Get current project tempo"""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get bridge status information"""
        return {
            "daw_type": self.daw_type.value,
            "connected": self.is_connected,
        }
