from pyMRI.gui.menu.tab import GuiTab

from pyMRI.processing import (
    Unit,
    InterpolateModes,
    ORIENTATIONS,
    CONVERT_STEP,
    REORIENT_STEP,
    INTERPOLATE_STEP,
)

from imgui_bundle import imgui


class AdjustmentTab(GuiTab):

    def __init__(self):
        super().__init__("Adjust")

    def update(self):
        pass
        # Convert

        # Reorient Step
        imgui.text("Orientation")
        if REORIENT_STEP.has_processed:
            imgui.same_line()
            if imgui.begin_combo("##orient", REORIENT_STEP.data.orientation):
                for orientation in ORIENTATIONS:
                    is_selectable = len(orientation) == sum(
                        i > 1 for i in REORIENT_STEP.data.voxel_counts
                    )
                    if not is_selectable:
                        continue

                    is_selected = orientation == REORIENT_STEP.data.orientation
                    select, is_selected = imgui.selectable(
                        f"{orientation}", is_selected
                    )
                    if select:
                        REORIENT_STEP.new_orientation = orientation
                    if is_selected:
                        imgui.set_item_default_focus()
                imgui.end_combo()

        # Interpolate Step
        imgui.text("Interpolation")
        if INTERPOLATE_STEP.has_processed:
            if imgui.begin_combo("##interp", str(INTERPOLATE_STEP.mode)):
                for interp in InterpolateModes:
                    is_selected = interp == INTERPOLATE_STEP.mode
                    select, is_selected = imgui.selectable(f"{interp}", is_selected)
                    if select:
                        INTERPOLATE_STEP.mode = interp
                    if is_selected:
                        imgui.set_item_default_focus()
                imgui.end_combo()
