"""Audio service for ClynBoozle application using pygame."""

from typing import Optional, Callable
import os
import tempfile
import threading
import time
import pygame

from ..config.settings import GameConfig
from ..utils.exceptions import AudioError


class AudioService:
    """Service for handling audio playback using pygame."""

    def __init__(self) -> None:
        """Initialize the audio service."""
        self._initialized = False
        self._current_sound: Optional[pygame.mixer.Sound] = None
        self._temp_files: list[str] = []
        self._position = 0.0
        self._length = 0.0
        self._is_playing = False
        self._is_paused = False
        self._position_callback: Optional[Callable[[float], None]] = None
        self._update_thread: Optional[threading.Thread] = None
        self._stop_update = False

        self._initialize_pygame()

    def _initialize_pygame(self) -> None:
        """Initialize pygame mixer."""
        try:
            pygame.mixer.init(
                frequency=GameConfig.AUDIO_FREQUENCY,
                size=GameConfig.AUDIO_SIZE,
                channels=GameConfig.AUDIO_CHANNELS,
                buffer=GameConfig.AUDIO_BUFFER,
            )
            self._initialized = True
        except pygame.error as e:
            raise AudioError(f"Failed to initialize audio system: {e}")

    def is_initialized(self) -> bool:
        """Check if audio system is initialized."""
        return self._initialized

    def load_audio_from_data(self, audio_data: bytes, filename: str = "audio.wav") -> None:
        """Load audio from raw data."""
        if not self._initialized:
            raise AudioError("Audio system not initialized")

        try:
            # Create temporary file
            file_ext = os.path.splitext(filename)[1] or ".wav"
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            temp_file.write(audio_data)
            temp_file.close()

            # Track temp file for cleanup
            self._temp_files.append(temp_file.name)

            # Load sound
            self._current_sound = pygame.mixer.Sound(temp_file.name)
            self._length = self._current_sound.get_length()
            self._position = 0.0
            self._is_playing = False
            self._is_paused = False

        except Exception as e:
            raise AudioError(f"Failed to load audio: {e}")

    def load_audio_from_file(self, file_path: str) -> None:
        """Load audio from file path."""
        if not self._initialized:
            raise AudioError("Audio system not initialized")

        if not os.path.exists(file_path):
            raise AudioError(f"Audio file not found: {file_path}")

        try:
            self._current_sound = pygame.mixer.Sound(file_path)
            self._length = self._current_sound.get_length()
            self._position = 0.0
            self._is_playing = False
            self._is_paused = False

        except Exception as e:
            raise AudioError(f"Failed to load audio file: {e}")

    def play(self, start_position: float = 0.0) -> None:
        """Play the loaded audio from specified position."""
        if not self._current_sound:
            raise AudioError("No audio loaded")

        try:
            if self._is_paused:
                # Resume from pause
                pygame.mixer.unpause()
                self._is_paused = False
            else:
                # Start playing (pygame doesn't support seeking easily)
                self._current_sound.play()
                self._position = start_position

            self._is_playing = True
            self._start_position_updates()

        except Exception as e:
            raise AudioError(f"Failed to play audio: {e}")

    def pause(self) -> None:
        """Pause audio playback."""
        if not self._is_playing:
            return

        try:
            pygame.mixer.pause()
            self._is_paused = True
            self._stop_position_updates()

        except Exception as e:
            raise AudioError(f"Failed to pause audio: {e}")

    def stop(self) -> None:
        """Stop audio playback."""
        try:
            pygame.mixer.stop()
            self._is_playing = False
            self._is_paused = False
            self._position = 0.0
            self._stop_position_updates()

        except Exception as e:
            raise AudioError(f"Failed to stop audio: {e}")

    def set_position(self, position: float) -> None:
        """Set playback position (limited support in pygame)."""
        if position < 0 or position > self._length:
            raise AudioError("Position out of range")

        # pygame doesn't support true seeking, so we restart from beginning
        # This is a limitation we'll note in the UI
        was_playing = self._is_playing
        self.stop()
        self._position = position

        if was_playing:
            self.play(position)

    def get_position(self) -> float:
        """Get current playback position."""
        return self._position

    def get_length(self) -> float:
        """Get total audio length."""
        return self._length

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self._is_playing and not self._is_paused

    def is_paused(self) -> bool:
        """Check if audio is paused."""
        return self._is_paused

    def set_position_callback(self, callback: Optional[Callable[[float], None]]) -> None:
        """Set callback function for position updates."""
        self._position_callback = callback

    def _start_position_updates(self) -> None:
        """Start position update thread."""
        if self._update_thread and self._update_thread.is_alive():
            return

        self._stop_update = False
        self._update_thread = threading.Thread(target=self._update_position_loop)
        self._update_thread.daemon = True
        self._update_thread.start()

    def _stop_position_updates(self) -> None:
        """Stop position update thread."""
        self._stop_update = True
        if self._update_thread:
            self._update_thread.join(timeout=1.0)

    def _update_position_loop(self) -> None:
        """Position update loop running in separate thread."""
        update_interval = GameConfig.AUDIO_UPDATE_INTERVAL / 1000.0  # Convert to seconds

        while not self._stop_update and self._is_playing:
            if not self._is_paused:
                self._position += update_interval

                # Check if playback has finished
                if self._position >= self._length:
                    self._position = self._length
                    self._is_playing = False
                    if self._position_callback:
                        self._position_callback(self._position)
                    break

                # Call position callback
                if self._position_callback:
                    self._position_callback(self._position)

            time.sleep(update_interval)

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop()
        self._stop_position_updates()

        # Clean up temporary files
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except OSError:
                pass  # Ignore cleanup errors

        self._temp_files.clear()
        self._current_sound = None

        if self._initialized:
            try:
                pygame.mixer.quit()
            except Exception:
                pass  # Ignore quit errors
            self._initialized = False

    def __del__(self) -> None:
        """Destructor to ensure cleanup."""
        self.cleanup()
