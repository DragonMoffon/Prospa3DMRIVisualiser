from __future__ import annotations

from typing import Callable
from enum import Enum

from arcade import get_window

from imgui_bundle import imgui


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

POPUP_FLAGS = (
    imgui.WindowFlags_.no_decoration |
    imgui.WindowFlags_.always_auto_resize |
    imgui.WindowFlags_.no_saved_settings |
    imgui.WindowFlags_.no_nav |
    imgui.WindowFlags_.no_collapse |
    imgui.WindowFlags_.no_move |
    imgui.WindowFlags_.no_focus_on_appearing
)

COLOR_TEXT_FLAG = imgui.Col_.text


class GuiPopup:

    def __init__(self, title: str, text: str, mode: WarningMode, responses: dict[str, Callable[[], None]]):
        self._win = get_window()
        self._mode = mode
        self._colour = WarningMode.to_colour(mode)


        self._title: str = title
        self._text: str = text

        self._buttons: dict[str, Callable[[], None]] = responses

    def update(self):
        viewport = imgui.get_main_viewport()
        work_pos = viewport.work_pos
        work_size = viewport.work_size
        window_pos = work_pos[0] + work_size[0]/2.0, work_pos[1] + work_size[1]/2.0
        window_pivot = 0.5, 0.5

        imgui.set_next_window_pos(window_pos, 1, window_pivot)
        imgui.set_next_window_bg_alpha(0.35)

        imgui.begin(self._title, False, POPUP_FLAGS)
        imgui.push_style_color(COLOR_TEXT_FLAG, self._colour)
        imgui.text(self._title)
        imgui.pop_style_color()

        self.build_body()
        self.build_buttons()

        imgui.end()

    def build_body(self):
        imgui.text_wrapped(self._text)

    def build_buttons(self):
        for name, callback in self._buttons.items():
            if imgui.button(name):
                callback()
            imgui.same_line()
