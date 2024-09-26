from pyMRI.gui.menu.tab import GuiTab

from pyMRI.processing import (
    FOURIER_STEP,
    PRE_SHIFT_STEP,
    POST_SHIFT_STEP,
    FourierMode,
    FourierNorm,
)

from imgui_bundle import imgui


class TransformTab(GuiTab):

    def __init__(self):
        super().__init__("Fourier")

    def update(self):
        # Shift
        imgui.text("Zero Frequency Shift")
        imgui.text("pre -")
        imgui.same_line()
        imgui.text("x:")
        imgui.same_line()
        changed, x = imgui.checkbox("##pre_x", PRE_SHIFT_STEP.shift_x)
        if changed:
            PRE_SHIFT_STEP.shift_x = x
        imgui.same_line()
        imgui.text("y:")
        imgui.same_line()
        changed, y = imgui.checkbox("##pre_y", PRE_SHIFT_STEP.shift_y)
        if changed:
            PRE_SHIFT_STEP.shift_y = y
        imgui.same_line()
        imgui.text("z:")
        imgui.same_line()
        changed, z = imgui.checkbox("##pre_z", PRE_SHIFT_STEP.shift_z)
        if changed:
            PRE_SHIFT_STEP.shift_z = z
        imgui.same_line()
        imgui.text("inverse:")
        imgui.same_line()
        changed, i = imgui.checkbox("##pre_i", PRE_SHIFT_STEP.inverse)
        if changed:
            PRE_SHIFT_STEP.inverse = i
        imgui.text("post -")
        imgui.same_line()
        imgui.text("x:")
        imgui.same_line()
        changed, x = imgui.checkbox("##post_x", POST_SHIFT_STEP.shift_x)
        if changed:
            POST_SHIFT_STEP.shift_x = x
        imgui.same_line()
        imgui.text("y:")
        imgui.same_line()
        changed, y = imgui.checkbox("##post_y", POST_SHIFT_STEP.shift_y)
        if changed:
            POST_SHIFT_STEP.shift_y = y
        imgui.same_line()
        imgui.text("z:")
        imgui.same_line()
        changed, z = imgui.checkbox("##post_z", POST_SHIFT_STEP.shift_z)
        if changed:
            POST_SHIFT_STEP.shift_z = z
        imgui.same_line()
        imgui.text("inverse:")
        imgui.same_line()
        changed, i = imgui.checkbox("##post_i", POST_SHIFT_STEP.inverse)
        if changed:
            POST_SHIFT_STEP.inverse = i
        # Filter
        pass
        # Fourier
        imgui.text("Fourier Transform")
        imgui.text("Transform Data:")
        imgui.same_line()
        changed, should = imgui.checkbox("##fourier-check", FOURIER_STEP.should)
        if changed:
            FOURIER_STEP.should = should

        if not should:
            imgui.begin_disabled()
        imgui.text("Inverse:")
        imgui.same_line()
        changed, inverse = imgui.checkbox("##fourier-inveerse", FOURIER_STEP.inverse)
        if changed:
            FOURIER_STEP.inverse = inverse
        imgui.text("Dimensions:")
        imgui.same_line()
        if imgui.begin_combo("##fourier-dim", FourierMode.to_str(FOURIER_STEP.mode)):
            for mode in FourierMode:
                is_selected = mode == FOURIER_STEP.mode
                select, is_selected = imgui.selectable(
                    f"{FourierMode.to_str(mode)}", is_selected
                )
                if select:
                    FOURIER_STEP.mode = mode
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()

        imgui.text("Normalisation:")
        imgui.same_line()
        if imgui.begin_combo("##fourier-norm", FOURIER_STEP.norm):
            for norm in FourierNorm:
                is_selected = norm == FOURIER_STEP.norm
                select, is_selected = imgui.selectable(norm, is_selected)
                if select:
                    FOURIER_STEP.norm = norm
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()
        if not should:
            imgui.end_disabled()
