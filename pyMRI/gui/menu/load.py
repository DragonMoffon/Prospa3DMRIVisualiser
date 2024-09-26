from imgui_bundle import imgui

from pyMRI.gui.menu.tab import GuiTab
from pyMRI.processing import Unit, ORIENTATIONS, FILE_LOADER_STEP


class LoadingTab(GuiTab):

    def __init__(self):
        super().__init__("Load")

    def update(self):
        imgui.text("Data File:")
        x, _ = imgui.get_content_region_avail()
        imgui.push_item_width(x - 80.0)
        load_data, path = imgui.input_text(
            "##data file",
            FILE_LOADER_STEP.data_path or "",
            imgui.InputTextFlags_.enter_returns_true,
        )
        imgui.pop_item_width()
        imgui.same_line()
        browse_data = imgui.button("browse##data", (70.0, 0.0))

        if load_data:
            FILE_LOADER_STEP.data_path = path
            FILE_LOADER_STEP.load_data = True
        elif browse_data:
            FILE_LOADER_STEP.data_path = None  # tiggers a fetch
            FILE_LOADER_STEP.load_data = True
        elif FILE_LOADER_STEP.data_path != path:
            FILE_LOADER_STEP.data_path = path

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
            load_para, path = imgui.input_text(
                "##parameter file",
                FILE_LOADER_STEP.parameter_path or "",
                imgui.InputTextFlags_.enter_returns_true,
            )
            imgui.pop_item_width()
            imgui.same_line()
            browse_para = imgui.button("browse##para", (70.0, 0.0))

            if load_para:
                FILE_LOADER_STEP.parameter_path = path
                FILE_LOADER_STEP.load_data = True
            elif browse_para:
                FILE_LOADER_STEP.parameter_path = None  # Triggers a file loading fetch
                FILE_LOADER_STEP.load_data = True
            elif FILE_LOADER_STEP.parameter_path != path:
                FILE_LOADER_STEP.parameter_path = path

            if not use_parameter_file:
                imgui.end_disabled()

        disabled = not FILE_LOADER_STEP.has_processed
        if disabled:
            imgui.begin_disabled()

        # Voxel Count
        counts = "No Data" if disabled else FILE_LOADER_STEP.data.voxel_counts
        imgui.text(f"Voxel Count: {counts}")

        # Orientation
        imgui.text("Orientation")
        orient = FILE_LOADER_STEP.orient_override or "No Data"
        imgui.same_line()
        changed = False
        if imgui.begin_combo("##orient", orient):
            for orientation in ORIENTATIONS:
                is_selectable = len(orientation) == len(orient)
                if not is_selectable:
                    continue

                is_selected = orientation == orient
                select, is_selected = imgui.selectable(f"{orientation}", is_selected)
                if select:
                    FILE_LOADER_STEP.orient_override = orientation
                    changed = True
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()
        if changed:
            FILE_LOADER_STEP.load_data = True

        # Dimensions
        imgui.text("Dimensions:")
        imgui.same_line()
        voxel_dimensions = FILE_LOADER_STEP.dimension_override or (float("inf"),) * 3
        changed, dimensions = imgui.input_float3(
            "##dimension",
            voxel_dimensions,
            flags=imgui.InputTextFlags_.enter_returns_true,
        )
        if voxel_dimensions[0] != float("inf"):
            FILE_LOADER_STEP.dimension_override = tuple(dimensions)
            if changed:
                FILE_LOADER_STEP.load_data = True

        # Units
        imgui.text("Units:")
        imgui.same_line()
        voxel_unit = FILE_LOADER_STEP.unit_override or Unit.MM
        changed = False
        if imgui.begin_combo("##unit", Unit.to_str(voxel_unit)):
            for unit in Unit:
                is_selected = unit == voxel_unit
                select, is_selectable = imgui.selectable(
                    f"{Unit.to_str(unit)}", is_selected
                )
                if select:
                    FILE_LOADER_STEP.unit_override = unit
                    changed = True
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()

        if changed:
            FILE_LOADER_STEP.load_data = True

        if disabled:
            imgui.end_disabled()
