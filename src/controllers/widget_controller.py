from src.widgets import histogram_widget as histogram_widget
from src.widgets import image_table_widget as image_table_widget


class WidgetController:
    open_windows = []

    def __init__(self, root):
        self.root = root

        root.menu_controller.open_histogram_eh.add(self.open_histogram_widget)

        root.menu_controller.open_image_table_eh.add(self.open_image_table_widget)

    def open_histogram_widget(self):
        new_histogram = histogram_widget.HistogramWidget(self.root)
        self.open_windows.append(new_histogram)

    def open_image_table_widget(self):
        new_image_table = image_table_widget.ImageTableWidget(self.root)
        self.open_windows.append(new_image_table)
