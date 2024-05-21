import imgui
from imgui.integrations.pyglet import create_renderer

from arcade import get_window


class GuiMenu:

    def __init__(self):
        self._win = get_window()
        imgui.create_context()
        imgui.get_io().display_size = self._win.width // 4, self._win.height // 4
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        self._renderer = create_renderer(self._win)
        self.show = True

        self._location: int = 0b00

        self._tabs: tuple = ()

    def toggle(self):
        self.show = not self.show

    def draw(self):
        if self.show:
            self._renderer.process_inputs()
            imgui.new_frame()

            PAD = 10.0
            win_flags = imgui.WINDOW_NO_DECORATION | imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_SAVED_SETTINGS | imgui.WINDOW_NO_FOCUS_ON_APPEARING | imgui.WINDOW_NO_NAV | imgui.WINDOW_NO_COLLAPSE

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

            win_flags |= imgui.WINDOW_NO_MOVE
            imgui.set_next_window_bg_alpha(0.35)

            with imgui.begin("Control Panel"):
                with imgui.begin_tab_bar("#tabs") as tab_bar:
                    if tab_bar.opened:
                        with imgui.begin_tab_item("Filtering") as filtering:
                            if filtering.selected:
                                imgui.text("Filtering")

                        with imgui.begin_tab_item("Colouring") as colouring:
                            if colouring.selected:
                                imgui.text("Colouring")

                        with imgui.begin_tab_item("Display") as display:
                            if display.selected:
                                imgui.text("Display")

                imgui.separator()

            imgui.show_demo_window()

            imgui.render()
            self._renderer.render(imgui.get_draw_data())
