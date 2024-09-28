from pyMRI.gui.menu.tab import GuiTab

from pyMRI.processing import (
    FOURIER_STEP,
    FILTER_STEP,
    PRE_SHIFT_STEP,
    POST_SHIFT_STEP,
    FILE_LOADER_STEP,
    FourierMode,
    FourierNorm,
)

from imgui_bundle import imgui


class TransformTab(GuiTab):

    def __init__(self):
        super().__init__("Fourier")
        self.pair_shifts = False

    def update(self):
        # Shift
        imgui.text("Zero Frequency Shift")
        imgui.same_line()
        _, self.pair_shifts = imgui.checkbox("pair shifts", self.pair_shifts)

        win_width = imgui.get_window_width()
        slider_width = win_width * 0.68 / 3.0
        sx, sy, sz = (
            (0, 0, 0)
            if not FILE_LOADER_STEP.has_processed
            else FILE_LOADER_STEP.data.voxel_data.shape
        )
        imgui.text("pre transform: ")
        imgui.same_line()
        imgui.push_item_width(slider_width)
        cx, x = imgui.slider_int("##pre-shift-x", PRE_SHIFT_STEP.shifts[0], -sx, sx)
        imgui.same_line()
        cy, y = imgui.slider_int("##pre-shift-y", PRE_SHIFT_STEP.shifts[1], -sy, sy)
        imgui.same_line()
        cz, z = imgui.slider_int("##pre-shift-z", PRE_SHIFT_STEP.shifts[2], -sz, sz)
        imgui.pop_item_width()
        if cx or cy or cz:
            PRE_SHIFT_STEP.shifts = (x, y, z)
            if self.pair_shifts:
                POST_SHIFT_STEP.shifts = (-x, -y, -z)

        if self.pair_shifts:
            imgui.begin_disabled()

        imgui.text("post transform:")
        imgui.push_item_width(slider_width)
        imgui.same_line()
        cx, x = imgui.slider_int("##post-shift-x", POST_SHIFT_STEP.shifts[0], -sx, sx)
        imgui.same_line()
        cy, y = imgui.slider_int("##post-shift-y", POST_SHIFT_STEP.shifts[1], -sy, sy)
        imgui.same_line()
        cz, z = imgui.slider_int("##post-shift-z", POST_SHIFT_STEP.shifts[2], -sz, sz)
        imgui.pop_item_width()
        if cx or cy or cz:
            POST_SHIFT_STEP.shifts = (x, y, z)

        if self.pair_shifts:
            imgui.end_disabled()

        # Filter
        imgui.text("Low Pass")
        imgui.same_line()
        changed, low = imgui.checkbox("##low-pass", FILTER_STEP.low_pass)
        if changed:
            FILTER_STEP.low_pass = low
        if not low:
            imgui.begin_disabled()
        imgui.same_line()
        imgui.text("radius")
        imgui.same_line()
        changed, low_rad = imgui.slider_float(
            "##low-pass-r", FILTER_STEP.low_pass_radius, 0.0, 100.0
        )
        if changed:
            FILTER_STEP.low_pass_radius = low_rad
        if not low:
            imgui.end_disabled()

        imgui.text("High Pass")
        imgui.same_line()
        changed, high = imgui.checkbox("##high-pass", FILTER_STEP.high_pass)
        if changed:
            FILTER_STEP.high_pass = high
        if not high:
            imgui.begin_disabled()
        imgui.same_line()
        imgui.text("radius")
        imgui.same_line()
        changed, high_rad = imgui.slider_float(
            "##high-pass-r", FILTER_STEP.high_pass_radius, 0.0, 100.0
        )
        if changed:
            FILTER_STEP.high_pass_radius = high_rad
        if not high:
            imgui.end_disabled()

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
