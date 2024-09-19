from imgui_bundle import imgui

from pyMRI.gui.menu.tab import GuiTab
from pyMRI.processing import Unit, ORIENTATIONS, FILE_LOADER_STEP


class LoadingTab(GuiTab):

    def __init__(self):
        super().__init__("Load")
        self._interum_data_path: str = FILE_LOADER_STEP.data_path or ""
        self._interum_parameter_path: str = FILE_LOADER_STEP.parameter_path or ""

    def update(self):
        imgui.text("Data File:")
        x, _ = imgui.get_content_region_avail()
        imgui.push_item_width(x - 80.0)
        load_data, self._interum_data_path = imgui.input_text(
            "##data file",
            self._interum_data_path,
            imgui.InputTextFlags_.enter_returns_true,
        )
        imgui.pop_item_width()
        imgui.same_line()
        browse_data = imgui.button("browse##data", (70.0, 0.0))

        if load_data:
            FILE_LOADER_STEP.data_path = self._interum_data_path
        elif browse_data:
            FILE_LOADER_STEP.data_path = None  # Triggers a file loading fetch
            self._interum_data_path = FILE_LOADER_STEP.data_path or ""

        if FILE_LOADER_STEP.can_use_parameter_file:
            # Use parameter file []
            # Show only if can use parameter file (using .xd file)
            imgui.text("Use Parameter File")
            imgui.same_line()
            exclude_changed, use_parameter_file = imgui.checkbox(
                "##use paramenter file", not FILE_LOADER_STEP.exclude_parameter_file
            )
            if exclude_changed:
                FILE_LOADER_STEP.exclude_parameter_file = not use_parameter_file

            if not use_parameter_file:
                imgui.begin_disabled()

            # Parameter File: [file loc] {browse button}
            imgui.text("Parameter File:")
            x, _ = imgui.get_content_region_avail()
            imgui.push_item_width(x - 80.0)
            load_para, self._interum_parameter_path = imgui.input_text(
                "##parameter file",
                self._interum_parameter_path,
                imgui.InputTextFlags_.enter_returns_true,
            )
            imgui.pop_item_width()
            imgui.same_line()
            browse_para = imgui.button("browse##para", (70.0, 0.0))

            if load_para:
                FILE_LOADER_STEP.parameter_path = self._interum_parameter_path or None
            elif browse_para:
                FILE_LOADER_STEP.parameter_path = None  # Triggers a file loading fetch
                self._interum_parameter_path = FILE_LOADER_STEP.parameter_path or ""

            if not use_parameter_file:
                imgui.end_disabled()

        if not FILE_LOADER_STEP.has_processed:
            return

        # Orientation
        imgui.text("Orientation")
        imgui.same_line()
        if imgui.begin_combo("##orient", FILE_LOADER_STEP.data.orientation):
            for orientation in ORIENTATIONS:
                is_selectable = len(orientation) == sum(
                    i > 1 for i in FILE_LOADER_STEP.data.voxel_counts
                )
                if not is_selectable:
                    continue

                is_selected = orientation == FILE_LOADER_STEP.data.orientation
                select, is_selected = imgui.selectable(f"{orientation}", is_selected)
                if select:
                    FILE_LOADER_STEP.orient_override = orientation
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()

        # Dimensions
        imgui.text("Dimensions:")
        imgui.same_line()
        changed, dimensions = imgui.input_float3(
            "##dimension", FILE_LOADER_STEP.data.voxel_dimensions
        )
        if changed:
            FILE_LOADER_STEP.dimension_override = tuple(dimensions)

        # Units
        imgui.text("Units:")
        imgui.same_line()
        if imgui.begin_combo("##unit", Unit.to_str(FILE_LOADER_STEP.data.voxel_unit)):
            for unit in Unit:
                is_selected = unit == FILE_LOADER_STEP.data.voxel_unit
                select, is_selectable = imgui.selectable(
                    f"{Unit.to_str(unit)}", is_selected
                )
                if select:
                    FILE_LOADER_STEP.unit_override = unit
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()
