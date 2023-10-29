import importlib
from enum import Enum
from functools import partial


class Widget(Enum):
    RENDERER = ("src.widgets.renderer_widget", "RendererWidget")
    IMAGE_TABLE = ("src.widgets.image_table_widget", "ImageTableWidget")
    CONTOURS = ("src.widgets.contour_widget", "ContourWidget")
    CATALOGUE = ("src.widgets.catalogue_widget", "CatalogueWidget")
    STATISTICS = ("src.widgets.statistics_widget", "StatisticsWidget")

    HIPS_SELECT = ("src.widgets.hips_selector_widget", "HipsSelectorWidget")

    def __init__(self, module_path, class_name):
        self._value = None
        self.module_path = module_path
        self.class_name = class_name

    @property
    def value(self):
        if self._value is None:
            module = importlib.import_module(self.module_path)
            self._value = getattr(module, self.class_name)
        return self._value


class WidgetController:
    def __init__(self, root):
        self.root = root
        self.open_windows = {}

        root.menu_controller.open_widget_eh.add(self.open_widget)

    def open_widget(self, widget):
        if widget not in self.open_windows:
            try:
                self.open_windows[widget] = widget.value(self.root)
            except Exception:
                return

            self.open_windows[widget].on_close_eh.add(
                partial(self.close_widget, widget)
            )

        def focus_window(window):
            window.wm_state("normal")
            window.focus_set()

        self.open_windows[widget].after(1, focus_window(self.open_windows[widget]))

    def close_widget(self, widget):
        if widget in self.open_windows:
            del self.open_windows[widget]

    def __getitem__(self, widget):
        return self.open_windows.get(widget)
