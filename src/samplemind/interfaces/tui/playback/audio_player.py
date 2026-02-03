"""
Audio Playback & Transport Controls for SampleMind TUI
Play, pause, seek, and control audio playback
"""

import logging
from typing import Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PlaybackState(Enum):
    """Playback state"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    SEEKING = "seeking"


class LoopMode(Enum):
    """Loop modes"""
    OFF = "off"
    LOOP_ALL = "loop_all"
    LOOP_SELECTION = "loop_selection"


@dataclass
class PlaybackStats:
    """Playback statistics"""
    current_position: float = 0.0  # In seconds
    duration: float = 0.0
    playback_rate: float = 1.0
    volume: int = 100  # 0-100
    loop_mode: LoopMode = LoopMode.OFF
    is_muted: bool = False


class AudioPlayer:
    """Audio playback and transport control"""

    def __init__(self, audio_data: Optional[List[float]] = None, sample_rate: int = 44100) -> None:
        """
        Initialize audio player

        Args:
            audio_data: Audio samples for playback
            sample_rate: Sample rate in Hz
        """
        self.audio_data = audio_data or []
        self.sample_rate = sample_rate
        self.state = PlaybackState.STOPPED
        self.stats = PlaybackStats()

        # Callbacks
        self.on_state_change: Optional[Callable] = None
        self.on_position_change: Optional[Callable] = None

    def load_audio(self, audio_data: List[float], sample_rate: int = 44100) -> None:
        """Load audio data"""
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.stats.duration = len(audio_data) / sample_rate
        self.stats.current_position = 0.0
        logger.info(f"Loaded audio: {self.stats.duration:.2f}s @ {sample_rate}Hz")

    def play(self) -> bool:
        """Start playback"""
        if not self.audio_data:
            logger.warning("No audio loaded")
            return False

        self.state = PlaybackState.PLAYING
        logger.info("Playback started")

        if self.on_state_change:
            self.on_state_change(self.state)

        return True

    def pause(self) -> bool:
        """Pause playback"""
        if self.state != PlaybackState.PLAYING:
            return False

        self.state = PlaybackState.PAUSED
        logger.info("Playback paused")

        if self.on_state_change:
            self.on_state_change(self.state)

        return True

    def resume(self) -> bool:
        """Resume from pause"""
        if self.state != PlaybackState.PAUSED:
            return False

        self.state = PlaybackState.PLAYING
        logger.info("Playback resumed")

        if self.on_state_change:
            self.on_state_change(self.state)

        return True

    def stop(self) -> bool:
        """Stop playback and reset position"""
        self.state = PlaybackState.STOPPED
        self.stats.current_position = 0.0
        logger.info("Playback stopped")

        if self.on_state_change:
            self.on_state_change(self.state)

        return True

    def seek(self, position_seconds: float) -> bool:
        """
        Seek to position

        Args:
            position_seconds: Position in seconds

        Returns:
            True if seek was successful
        """
        if position_seconds < 0 or position_seconds > self.stats.duration:
            logger.warning(f"Seek out of range: {position_seconds}")
            return False

        self.stats.current_position = position_seconds
        logger.debug(f"Seeked to: {position_seconds:.2f}s")

        if self.on_position_change:
            self.on_position_change(position_seconds)

        return True

    def seek_percentage(self, percentage: float) -> bool:
        """
        Seek to percentage of duration

        Args:
            percentage: 0.0-1.0

        Returns:
            True if seek was successful
        """
        if percentage < 0 or percentage > 1.0:
            logger.warning(f"Seek percentage out of range: {percentage}")
            return False

        position = percentage * self.stats.duration
        return self.seek(position)

    def set_volume(self, volume: int) -> bool:
        """
        Set volume

        Args:
            volume: Volume 0-100

        Returns:
            True if volume was set
        """
        if volume < 0 or volume > 100:
            logger.warning(f"Volume out of range: {volume}")
            return False

        self.stats.volume = volume
        logger.debug(f"Volume set to: {volume}")
        return True

    def set_playback_rate(self, rate: float) -> bool:
        """
        Set playback rate (speed)

        Args:
            rate: Playback rate (0.5x to 2x)

        Returns:
            True if rate was set
        """
        if rate < 0.5 or rate > 2.0:
            logger.warning(f"Playback rate out of range: {rate}")
            return False

        self.stats.playback_rate = rate
        logger.debug(f"Playback rate set to: {rate}x")
        return True

    def toggle_mute(self) -> bool:
        """Toggle mute on/off"""
        self.stats.is_muted = not self.stats.is_muted
        status = "muted" if self.stats.is_muted else "unmuted"
        logger.debug(f"Audio {status}")
        return True

    def set_loop_mode(self, loop_mode: LoopMode) -> None:
        """Set loop mode"""
        self.stats.loop_mode = loop_mode
        logger.debug(f"Loop mode set to: {loop_mode.value}")

    def get_position_percentage(self) -> float:
        """Get current position as percentage (0.0-1.0)"""
        if self.stats.duration == 0:
            return 0.0
        return self.stats.current_position / self.stats.duration

    def get_time_remaining(self) -> float:
        """Get time remaining in seconds"""
        return max(0, self.stats.duration - self.stats.current_position)

    def is_playing(self) -> bool:
        """Check if currently playing"""
        return self.state == PlaybackState.PLAYING

    def is_paused(self) -> bool:
        """Check if currently paused"""
        return self.state == PlaybackState.PAUSED

    def format_time(self, seconds: float) -> str:
        """Format seconds to MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def get_playback_info(self) -> str:
        """Get formatted playback information"""
        time_str = self.format_time(self.stats.current_position)
        duration_str = self.format_time(self.stats.duration)
        rate_str = f"{self.stats.playback_rate:.1f}x"
        volume_str = f"{self.stats.volume}%"
        state_str = self.state.value
        loop_str = self.stats.loop_mode.value

        return (
            f"[{state_str}] {time_str} / {duration_str} | "
            f"Speed: {rate_str} | Volume: {volume_str} | Loop: {loop_str}"
        )

    def print_info(self) -> str:
        """Print playback information"""
        time_str = self.format_time(self.stats.current_position)
        duration_str = self.format_time(self.stats.duration)
        position_pct = self.get_position_percentage()
        progress = "█" * int(position_pct * 20) + "░" * (20 - int(position_pct * 20))

        lines = [
            "╔════════════════════════════════════════╗",
            "║        PLAYBACK INFORMATION           ║",
            "╠════════════════════════════════════════╣",
            f"║ Status: {self.state.value:<32} ║",
            f"║ {progress} {position_pct*100:>5.1f}%    ║",
            f"║ Time: {time_str} / {duration_str:<24} ║",
            f"║ Volume: {self.stats.volume:>3}% | Speed: {self.stats.playback_rate:.1f}x          ║",
            f"║ Loop: {self.stats.loop_mode.value:<33} ║",
            "╚════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


# Global singleton instance
_audio_player: Optional[AudioPlayer] = None


def get_audio_player(
    audio_data: Optional[List[float]] = None, sample_rate: int = 44100
) -> AudioPlayer:
    """Get or create audio player singleton"""
    global _audio_player
    if _audio_player is None:
        _audio_player = AudioPlayer(audio_data, sample_rate)
    return _audio_player
