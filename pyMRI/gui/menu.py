import imgui
from imgui.integrations.pyglet import create_renderer

from arcade import get_window


class GuiMenu:

    def __init__(self):
        self._win = get_window()
        imgui.create_context()
        imgui.get_io().display_size = 100, 100
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        self._renderer = create_renderer(self._win)
        self.show = True

        self._tabs: tuple = ()

    def toggle(self):
        self.show = not self.show

    def draw(self):
        if self.show:
            self._renderer.process_inputs()
            imgui.new_frame()

            with imgui.begin("Control Panel"):
                with imgui.begin_tab_bar("#tabs") as tab_bar:
                    with imgui.begin_tab_item("Filtering") as filtering:
                        imgui.text("Filtering")

                    with imgui.begin_tab_item("Colouring") as colouring:
                        imgui.text("Colouring")

                    with imgui.begin_tab_item("Display") as display:
                        imgui.text("Display")

            imgui.separator()

            imgui.show_demo_window()

            imgui.render()
            self._renderer.render(imgui.get_draw_data())


