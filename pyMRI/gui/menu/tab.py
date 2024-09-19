from imgui_bundle import imgui


class GuiTab:

    def __init__(self, title: str):
        self.title: str = title

    def update(self):
        imgui.separator()
