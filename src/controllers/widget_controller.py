from enum import Enum
from functools import partial

from src.widgets import (
    catalogue_widget,
    contour_widget,
    hips_selector_widget,
    image_table_widget,
    renderer_widget,
    statistics_widget,
)


class Widget(Enum):
    RENDERER = renderer_widget.RendererWidget
    IMAGE_TABLE = image_table_widget.ImageTableWidget
    CONTOURS = contour_widget.ContourWidget
    CATALOGUE = catalogue_widget.CatalogueWidget
    STATISTICS = statistics_widget.StatisticsWidget

    HIPS_SELECT = hips_selector_widget.HipsSelectorWidget


class WidgetController:
    def __init__(self, root):
        self.root = root
        self.open_windows = {}

        root.menu_controller.open_widget_eh.add(self.open_widget)

    def open_widget(self, widget):
        if widget not in self.open_windows:
            self.open_windows[widget] = widget.value(self.root)
            self.open_windows[widget].on_close_eh.add(
                partial(self.close_widget, widget)
            )

    def close_widget(self, widget):
        if widget in self.open_windows:
            del self.open_windows[widget]

    def __getitem__(self, widget):
        return self.open_windows.get(widget)
