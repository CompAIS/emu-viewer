from src.widgets import image_table_widget, renderer_widget


class WidgetController:
    def __init__(self, root):
        self.root = root
        self.open_windows = []

        root.menu_controller.open_renderer_eh.add(self.open_renderer_widget)

        root.menu_controller.open_image_table_eh.add(self.open_image_table_widget)

    def open_renderer_widget(self):
        new_renderer = renderer_widget.RendererWidget(self.root)
        self.open_windows.append(new_renderer)

    def open_image_table_widget(self):
        new_image_table = image_table_widget.ImageTableWidget(self.root)
        self.open_windows.append(new_image_table)
