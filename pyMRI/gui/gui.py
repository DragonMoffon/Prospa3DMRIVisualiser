from imgui_bundle import imgui
from pyMRI._distutil_workaround import PygletProgrammablePipelineRenderer
from arcade import Window as ArcadeWindow, get_window


from pyMRI.gui.popups.popup import GuiPopup, WarningMode
from pyMRI.gui.menu.menu import GuiMenu
from pyMRI.gui.menu.tab import GuiTab


class Gui:

    def __init__(self):
        self._win: ArcadeWindow = None
        self._renderer = None

        self._menu = None
        self._popups: list[GuiPopup] = []

    def initialise(self):
        imgui.create_context()
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        self._win = get_window()
        self._renderer = PygletProgrammablePipelineRenderer(self._win)
        self._menu = GuiMenu(())

    def update(self):
        self._renderer.process_inputs()
        imgui.new_frame()
        if self._popups:
            self._popups[-1].update()
        else:
            self._menu.update()

        imgui.end_frame()

    def draw(self):
        imgui.render()
        self._renderer.render(imgui.get_draw_data())

    def enable_menu(self):
        self._win.set_exclusive_mouse(False)
        self._menu.enable()

    def disable_menu(self):
        self._win.set_exclusive_mouse(True)
        self._menu.disable()

    def push_popup(self, popup: GuiPopup):
        self._popups.append(popup)
        self._win.set_exclusive_mouse(False)
        self._menu.disable()

    def pop_popup(self):
        self._popups.pop(-1)
        if not self._popups:
            self.enable_menu()

    @property
    def show_menu(self) -> bool:
        return not self._menu.is_disabled

    @property
    def exclusive(self) -> bool:
        return len(self._popups) > 0 or self.show_menu

    @property
    def capturing_input(self) -> bool:
        return imgui.get_io().want_capture_keyboard

    @property
    def capturing_mouse(self) -> bool:
        return imgui.get_io().want_capture_mouse

GUI = Gui()
