import imgui
from imgui.integrations.pyglet import create_renderer

from arcade import get_window

from pyMRI.gui.tab import GuiTab


class GuiMenu:

    def __init__(self, tabs: tuple[GuiTab, ...]):
        self._win = get_window()
        self._renderer = create_renderer(self._win)
        self.is_disabled: bool = False

        self._location: int = 0b00

        self._tabs: tuple[GuiTab, ...] = tabs

    def toggle(self):
        self.is_disabled = not self.is_disabled

    def enable(self):
        self.is_disabled = False

    def disable(self):
        self.is_disabled = True

    def update(self):
        if self.is_disabled:
            return

        PAD = 10.0
        win_flags = imgui.WINDOW_NO_DECORATION | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SAVED_SETTINGS | imgui.WINDOW_NO_FOCUS_ON_APPEARING | imgui.WINDOW_NO_NAV | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_MOVE

        viewport = imgui.get_main_viewport()
        work_pos = viewport.work_pos
        work_size = viewport.work_size
        window_pos = (
            work_pos[0] + work_size[0] - PAD if self._location & 0b01 else work_pos.x + PAD,
            work_pos[1] + work_size[1] - PAD if self._location & 0b10 else work_pos.y + PAD
        )
        window_pivot = (
            1.0 if self._location & 0b01 else 0.0,
            1.0 if self._location & 0b10 else 0.0
        )

        imgui.set_next_window_position(window_pos[0], window_pos[1], imgui.ALWAYS, window_pivot[0], window_pivot[1])
        imgui.set_next_window_size(work_size[0] / 2, work_size[1] / 2)
        imgui.set_next_window_bg_alpha(0.35)

        with imgui.begin("Control Panel", False, win_flags):
            with imgui.begin_tab_bar("#tabs") as tab_bar:
                if tab_bar.opened:
                    for tab in self._tabs:
                        with imgui.begin_tab_item(tab.title) as tab_:
                            if tab_.selected:
                                tab.update()
