"""Question dialog component for displaying questions with media support."""

import tkinter as tk
from tkinter import ttk
import tempfile
import os
from typing import Dict, Any, Optional, Callable
from PIL import Image, ImageTk

from .base_dialog import BaseDialog
from ..config.settings import Colors


class QuestionDialog(BaseDialog):
    """Dialog for displaying quiz questions with image and audio support."""

    def __init__(
        self,
        parent: tk.Widget,
        question_data: Dict[str, Any],
        on_correct: Optional[Callable] = None,
        on_incorrect: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        audio_initialized: bool = False,
        **kwargs,
    ):
        """
        Initialize the question dialog.

        Args:
            parent: Parent widget
            question_data: Dictionary containing question data and media
            on_correct: Callback for correct answer
            on_incorrect: Callback for incorrect answer
            on_close: Callback when dialog is closed
            audio_initialized: Whether pygame audio is available
        """
        self.question_data = question_data
        self.on_correct = on_correct
        self.on_incorrect = on_incorrect
        self.on_close = on_close
        self.audio_initialized = audio_initialized

        # Audio state tracking
        self.audio_state = {
            "is_playing": False,
            "is_paused": False,
            "position": 0.0,
            "update_job": None,
            "user_dragging": False,
            "was_playing_before_drag": False,
        }
        self.temp_audio_file = None
        self.sound_length = 0.0

        super().__init__(parent, title="Question", width=600, height=400, resizable=True, **kwargs)

    def build_content(self) -> tk.Widget:
        """Build the dialog content."""
        # Main content frame
        content_frame = tk.Frame(self.dialog, bg=Colors.BACKGROUND)
        content_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self._build_image_section(content_frame)
        self._build_audio_section(content_frame)
        self._build_question_section(content_frame)
        self._build_answer_section(content_frame)

        return content_frame

    def _build_image_section(self, parent: tk.Widget) -> None:
        """Build the image display section."""
        original_img = self.question_data.get("_question_pil", None)
        if not original_img:
            return

        img_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        img_frame.pack(pady=(0, 10), fill=tk.BOTH, expand=True)

        self.img_label = tk.Label(img_frame, bg=Colors.BACKGROUND, cursor="hand2")
        self.img_label.pack(expand=True)

        hint = tk.Label(
            img_frame,
            text="Click image to enlarge",
            font=("Arial", 10),
            fg="#888888",
            bg=Colors.BACKGROUND,
        )
        hint.pack()

        # Set up image resizing
        self._setup_image_resizing(img_frame, original_img)

        # Set up click handler for enlargement
        self.img_label.bind("<Button-1>", lambda e: self._show_enlarged_image(original_img))

    def _setup_image_resizing(self, img_frame: tk.Widget, original_img: Image.Image) -> None:
        """Set up debounced image resizing."""

        def do_resize():
            if not self.img_label.winfo_exists():
                return
            w = img_frame.winfo_width() - 20
            h = img_frame.winfo_height() - 30
            if w < 10 or h < 10:
                return

            iw, ih = original_img.size
            aspect = iw / ih
            if w / h > aspect:
                new_h = h
                new_w = int(h * aspect)
            else:
                new_w = w
                new_h = int(w / aspect)

            resized = original_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            self.img_label.configure(image=photo)
            self.img_label.image = photo

        def schedule_resize(event=None):
            if hasattr(self.dialog, "_resize_job"):
                self.dialog.after_cancel(self.dialog._resize_job)
            self.dialog._resize_job = self.dialog.after(100, do_resize)

        self.dialog.bind("<Configure>", schedule_resize)

    def _show_enlarged_image(self, original_img: Image.Image) -> None:
        """Show enlarged image in a new window."""
        enlarged_window = tk.Toplevel(self.dialog)
        enlarged_window.title("Enlarged Image")
        enlarged_window.configure(bg=Colors.BACKGROUND)
        enlarged_window.transient(self.dialog)
        enlarged_window.withdraw()

        sw, sh = enlarged_window.winfo_screenwidth(), enlarged_window.winfo_screenheight()
        iw, ih = original_img.size
        aspect = iw / ih
        max_w, max_h = int(sw * 0.9), int(sh * 0.9)

        if max_w / max_h > aspect:
            nh = max_h
            nw = int(max_h * aspect)
        else:
            nw = max_w
            nh = int(max_w / aspect)

        enlarged = original_img.resize((nw, nh), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(enlarged)

        lbl = tk.Label(enlarged_window, image=photo, bg=Colors.BACKGROUND)
        lbl.image = photo
        lbl.pack(padx=10, pady=10)

        # Center and show window
        enlarged_window.update_idletasks()
        x = (sw - enlarged_window.winfo_width()) // 2
        y = (sh - enlarged_window.winfo_height()) // 2
        enlarged_window.geometry(f"+{x}+{y}")
        enlarged_window.deiconify()

        # Close handlers
        lbl.bind("<Button-1>", lambda e: enlarged_window.destroy())
        enlarged_window.bind("<Escape>", lambda e: enlarged_window.destroy())

    def _build_audio_section(self, parent: tk.Widget) -> None:
        """Build the audio controls section."""
        audio_data = self.question_data.get("_question_audio", None)
        if not audio_data or not self.audio_initialized:
            return

        try:
            import pygame
        except ImportError:
            return

        audio_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        audio_frame.pack(pady=10, fill=tk.X)

        # Audio info
        audio_filename = self.question_data.get("_audio_filename", "Unknown")
        audio_info = tk.Label(
            audio_frame,
            text=f"Audio: {audio_filename}",
            font=("Arial", 12),
            bg=Colors.BACKGROUND,
            fg="#888888",
        )
        audio_info.pack(pady=(0, 5))

        self._setup_audio_controls(audio_frame, audio_data, audio_filename)

    def _setup_audio_controls(
        self, audio_frame: tk.Widget, audio_data: bytes, audio_filename: str
    ) -> None:
        """Set up audio playback controls."""
        import pygame

        try:
            # Create temporary file for pygame
            audio_ext = os.path.splitext(audio_filename)[1] or ".wav"
            self.temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=audio_ext)
            self.temp_audio_file.write(audio_data)
            self.temp_audio_file.close()

            # Load with pygame.music
            pygame.mixer.music.load(self.temp_audio_file.name)

            # Get duration
            temp_sound = pygame.mixer.Sound(self.temp_audio_file.name)
            self.sound_length = temp_sound.get_length()
            del temp_sound

            self._build_audio_controls_ui(audio_frame)

        except Exception as e:
            error_label = tk.Label(
                audio_frame,
                text=f"Audio error: {str(e)}",
                font=("Arial", 10),
                bg=Colors.BACKGROUND,
                fg="red",
            )
            error_label.pack()

    def _build_audio_controls_ui(self, audio_frame: tk.Widget) -> None:
        """Build the audio control interface."""
        # Controls container
        audio_controls = tk.Frame(audio_frame, bg=Colors.BACKGROUND)
        audio_controls.pack(pady=(0, 10))

        # Time & slider frame
        position_frame = tk.Frame(audio_frame, bg=Colors.BACKGROUND)
        position_frame.pack(fill=tk.X, pady=(0, 5))

        self.time_label = tk.Label(
            position_frame,
            text="00:00 / 00:00",
            font=("Arial", 10),
            bg=Colors.BACKGROUND,
            fg="#888888",
        )
        self.time_label.pack()

        self.position_slider = ttk.Scale(
            position_frame, from_=0, to=self.sound_length, orient=tk.HORIZONTAL, length=300
        )
        self.position_slider.pack(fill=tk.X, padx=20, pady=5)

        slider_help = tk.Label(
            position_frame,
            text="Drag slider to seek position",
            font=("Arial", 8),
            bg=Colors.BACKGROUND,
            fg="#666666",
        )
        slider_help.pack(pady=(0, 5))

        # Control buttons
        button_frame = tk.Frame(audio_controls, bg=Colors.BACKGROUND)
        button_frame.pack()

        self.play_btn = tk.Button(
            button_frame,
            text="Play",
            command=self._toggle_audio_playback,
            bg=Colors.BUTTON,
            fg=Colors.BUTTON_TEXT,
            font=("Arial", 12),
            padx=10,
            pady=5,
        )
        self.play_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = tk.Button(
            button_frame,
            text="Stop",
            command=self._stop_audio,
            bg=Colors.BUTTON,
            fg=Colors.BUTTON_TEXT,
            font=("Arial", 12),
            padx=10,
            pady=5,
            state="disabled",
        )
        self.stop_btn.pack(side=tk.LEFT)

        # Bind slider events
        self._setup_slider_events()

    def _setup_slider_events(self) -> None:
        """Set up slider drag events."""

        def on_slider_press(event):
            self.audio_state["user_dragging"] = True
            self.audio_state["was_playing_before_drag"] = (
                self.audio_state["is_playing"] and not self.audio_state["is_paused"]
            )
            if self.audio_state["was_playing_before_drag"]:
                self._pause_audio()

        def on_slider_release(event):
            if self.audio_state["user_dragging"]:
                new_pos = self.position_slider.get()
                self.audio_state["position"] = new_pos
                self.audio_state["user_dragging"] = False

                if self.audio_state["was_playing_before_drag"]:
                    self._play_audio()

        self.position_slider.bind("<Button-1>", on_slider_press)
        self.position_slider.bind("<ButtonRelease-1>", on_slider_release)

    def _toggle_audio_playback(self) -> None:
        """Toggle audio playback (play/pause)."""
        if not self.audio_state["is_playing"]:
            self._play_audio()
        elif self.audio_state["is_paused"]:
            self._resume_audio()
        else:
            self._pause_audio()

    def _play_audio(self) -> None:
        """Start audio playback."""
        import pygame

        if self.audio_state["position"] > 0:
            pygame.mixer.music.play(start=self.audio_state["position"])
        else:
            pygame.mixer.music.play()

        self.audio_state["is_playing"] = True
        self.audio_state["is_paused"] = False
        self.play_btn.configure(text="Pause")
        self.stop_btn.configure(state="normal")
        self._update_audio_position()

    def _pause_audio(self) -> None:
        """Pause audio playback."""
        import pygame

        pygame.mixer.music.pause()
        self.audio_state["is_paused"] = True
        self.play_btn.configure(text="Resume")
        if self.audio_state["update_job"]:
            self.dialog.after_cancel(self.audio_state["update_job"])
            self.audio_state["update_job"] = None

    def _resume_audio(self) -> None:
        """Resume audio playback."""
        import pygame

        pygame.mixer.music.unpause()
        self.audio_state["is_paused"] = False
        self.play_btn.configure(text="Pause")
        self._update_audio_position()

    def _stop_audio(self) -> None:
        """Stop audio playback."""
        import pygame

        pygame.mixer.music.stop()
        self.audio_state["is_playing"] = False
        self.audio_state["is_paused"] = False
        self.audio_state["position"] = 0.0
        self.position_slider.set(0.0)
        self.play_btn.configure(text="Play")
        self.stop_btn.configure(state="disabled")
        self.time_label.configure(text=f"00:00 / {self._format_time(self.sound_length)}")
        if self.audio_state["update_job"]:
            self.dialog.after_cancel(self.audio_state["update_job"])
            self.audio_state["update_job"] = None

    def _update_audio_position(self) -> None:
        """Update audio position display."""
        if not self.audio_state["is_playing"] or self.audio_state["is_paused"]:
            return

        self.audio_state["position"] += 0.1

        if self.audio_state["position"] > self.sound_length:
            self.audio_state["position"] = self.sound_length
            self._stop_audio()
            return

        if not self.audio_state["user_dragging"]:
            self.position_slider.set(self.audio_state["position"])

        self.time_label.configure(
            text=f"{self._format_time(self.audio_state['position'])} / {self._format_time(self.sound_length)}"
        )
        self.audio_state["update_job"] = self.dialog.after(100, self._update_audio_position)

    def _format_time(self, seconds: float) -> str:
        """Format time in MM:SS format."""
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

    def _build_question_section(self, parent: tk.Widget) -> None:
        """Build the question display section."""
        question_text = self.question_data.get("question", "")
        if not question_text:
            return

        question_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        question_frame.pack(pady=10, fill=tk.X)

        question_label = tk.Label(
            question_frame,
            text=f"Question: {question_text}",
            font=("Arial", 14, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT,
            wraplength=500,
            justify=tk.LEFT,
        )
        question_label.pack(anchor="w")

    def _build_answer_section(self, parent: tk.Widget) -> None:
        """Build the answer reveal and scoring section."""
        answer_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        answer_frame.pack(pady=20, fill=tk.X)

        # Answer display (initially hidden)
        self.answer_label = tk.Label(
            answer_frame,
            text="",
            font=("Arial", 12),
            bg=Colors.BACKGROUND,
            fg="#00AA00",
            wraplength=500,
            justify=tk.LEFT,
        )
        self.answer_label.pack(anchor="w", pady=(0, 10))

        # Control buttons
        button_frame = tk.Frame(answer_frame, bg=Colors.BACKGROUND)
        button_frame.pack()

        reveal_btn = tk.Button(
            button_frame,
            text="Reveal Answer",
            command=self._reveal_answer,
            bg=Colors.BUTTON,
            fg=Colors.BUTTON_TEXT,
            font=("Arial", 12),
            padx=15,
            pady=8,
        )
        reveal_btn.pack(side=tk.LEFT, padx=(0, 10))

        correct_btn = tk.Button(
            button_frame,
            text="Correct",
            command=self._mark_correct,
            bg="#00AA00",
            fg="white",
            font=("Arial", 12),
            padx=15,
            pady=8,
        )
        correct_btn.pack(side=tk.LEFT, padx=(0, 10))

        incorrect_btn = tk.Button(
            button_frame,
            text="Incorrect",
            command=self._mark_incorrect,
            bg="#CC0000",
            fg="white",
            font=("Arial", 12),
            padx=15,
            pady=8,
        )
        incorrect_btn.pack(side=tk.LEFT)

    def _reveal_answer(self) -> None:
        """Reveal the answer."""
        answer_text = self.question_data.get("answer", "No answer provided")
        self.answer_label.configure(text=f"Answer: {answer_text}")

    def _mark_correct(self) -> None:
        """Handle correct answer selection."""
        if self.on_correct:
            self.on_correct()
        self.close()

    def _mark_incorrect(self) -> None:
        """Handle incorrect answer selection."""
        if self.on_incorrect:
            self.on_incorrect()
        self.close()

    def close(self) -> None:
        """Close the dialog and clean up resources."""
        # Stop audio if playing
        if self.audio_state["is_playing"]:
            self._stop_audio()

        # Clean up temporary audio file
        if self.temp_audio_file and os.path.exists(self.temp_audio_file.name):
            try:
                os.unlink(self.temp_audio_file.name)
            except Exception:
                pass  # Ignore cleanup errors

        # Call parent close handler
        if self.on_close:
            self.on_close()

        super().close()
