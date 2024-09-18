from imgui_bundle import imgui

from arcade import get_window

from pyMRI.gui.menu.tab import GuiTab


class GuiMenu:

    def __init__(self, tabs: tuple[GuiTab, ...]):
        self._win = get_window()
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
        win_flags = (
            imgui.WindowFlags_.no_decoration |
            imgui.WindowFlags_.no_resize |
            imgui.WindowFlags_.no_saved_settings |
            imgui.WindowFlags_.no_nav |
            imgui.WindowFlags_.no_collapse |
            imgui.WindowFlags_.no_move |
            imgui.WindowFlags_.no_focus_on_appearing
        )
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
        window_size = (
            work_size[0] * 0.3,
            work_size[1] * 0.3
        )

        imgui.set_next_window_pos(window_pos, 1, window_pivot)
        imgui.set_next_window_size(window_size, 1)
        imgui.set_next_window_bg_alpha(0.35)

        imgui.begin("Control Panel", False, win_flags)
        if imgui.begin_tab_bar("#tabs"):
            for tab in self._tabs:
                selected, *_ = imgui.begin_tab_item(tab.title)
                if selected:
                    tab.update()
                imgui.end_tab_item()
            imgui.end_tab_bar()
        imgui.end()
