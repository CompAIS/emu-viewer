from enum import Enum
from functools import partial

from src.widgets import (
    contour_widget,
    hips_selector_widget,
    image_table_widget,
    renderer_widget,
)


class Widget(Enum):
    RENDERER = renderer_widget.RendererWidget
    IMAGE_TABLE = image_table_widget.ImageTableWidget
    CONTOURS = contour_widget.ContourWidget

    HIPS_SELECT = hips_selector_widget.HipsSelectorWidget


class WidgetController:
    def __init__(self, root):
        self.root = root
        self.open_windows = {}

        root.menu_controller.open_widget_eh.add(self.open_widget)

    def open_widget(self, widget):
        if widget.label not in self.open_windows:
            self.open_windows[widget.label] = widget(self.root)

            self.open_windows[widget.label].protocol(
                "WM_DELETE_WINDOW",
                partial(self.close_widget, widget),
            )

    def close_widget(self, widget):
        if widget.label in self.open_windows:
            self.open_windows[widget.label].destroy()
            self.open_windows[widget.label] = None

    def __getitem__(self, widget):
        return self.open_windows.get(widget.value)
