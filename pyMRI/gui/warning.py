from __future__ import annotations

from typing import Callable
from enum import Enum

import imgui


class WarningMode(Enum):
    WARNING = 0
    ERROR = 1
    INFO = 2

    @staticmethod
    def to_colour(mode: WarningMode):
        match mode:
            case WarningMode.WARNING:
                return (1.0, 1.0, 0, 1.0)
            case WarningMode.ERROR:
                return (255, 0, 0, 255)
            case WarningMode.INFO:
                return (255, 255, 255, 255)

    @staticmethod
    def to_str(mode: WarningMode):
        match mode:
            case WarningMode.WARNING:
                return "WARNING"
            case WarningMode.ERROR:
                return "ERROR"
            case WarningMode.INFO:
                return "INFO"


class GuiWarning:

    def __init__(self, imgui_renderer, name: str, text: str, mode: WarningMode,
                 continue_callback: Callable[[], None] = None, cancel_callback: Callable[[], None] = None,
                 closing: bool = True):
        self._renderer = imgui_renderer

        self._name: str = name
        self._text: str = text

        self._mode: WarningMode = mode

        self._continue_callback: Callable[[], None] = continue_callback
        self._cancel_callback: Callable[[], None] = cancel_callback

        self._is_closing: bool = closing  # If another system will close the dialog (no "ok" or "continue/cancel" buttons)
        self.is_popped: bool = False

    def update(self):
        win_flags = imgui.WINDOW_NO_DECORATION | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SAVED_SETTINGS | imgui.WINDOW_NO_FOCUS_ON_APPEARING | imgui.WINDOW_NO_NAV | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_MOVE

        viewport = imgui.get_main_viewport()
        work_pos = viewport.work_pos
        work_size = viewport.work_size
        window_pos = (
            work_pos[0] + work_size[0] / 2.0,
            work_pos[1] + work_size[1] / 2.0
        )
        window_pivot = (
            0.5,
            0.5
        )

        imgui.set_next_window_position(window_pos[0], window_pos[1], imgui.ALWAYS, window_pivot[0], window_pivot[1])
        imgui.set_next_window_size(work_size[0] / 8.0, work_size[1] / 8.0)

        imgui.set_next_window_bg_alpha(0.35)

        with imgui.begin(self._name, False, win_flags):
            imgui.push_style_color(imgui.COLOR_TEXT, *WarningMode.to_colour(self._mode))
            imgui.text(WarningMode.to_str(self._mode))
            imgui.pop_style_color()

            if self._continue_callback or self._cancel_callback:
                has_clicked_cont = imgui.button("Continue")
                imgui.same_line()
                has_clicked_canc = imgui.button("Cancel")
                self.is_popped = has_clicked_cont or has_clicked_canc
                if has_clicked_cont and self._continue_callback:
                    self._continue_callback()
                if has_clicked_canc and self._cancel_callback:
                    self._cancel_callback()
            elif self._is_closing:
                has_clicked_ok = imgui.button("Ok")
                self.is_popped = has_clicked_ok

    def draw(self):
        imgui.render()
        self._renderer.render(imgui.get_draw_data())