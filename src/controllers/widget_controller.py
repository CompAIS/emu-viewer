from src.widgets import image_table_widget, renderer_widget


class WidgetController:
    def __init__(self, root):
        self.root = root
        self.open_windows = {"Render Configuration": None, "Hips Survey Selector": None}

        root.menu_controller.open_render_eh.add(self.open_render_widget)

        root.menu_controller.open_image_table_eh.add(self.open_image_table_widget)

    def open_render_widget(self):
        if self.open_windows["Render Configuration"] is None:
            new_render_widget = renderer_widget.RendererWidget(self.root)
            self.open_windows["Render Configuration"] = new_render_widget

    def close_render_widget(self):
        if self.open_windows["Render Configuration"] is not None:
            self.open_windows["Render Configuration"].destroy()
            self.open_windows["Render Configuration"] = None

    def open_image_table_widget(self):
        new_image_table = image_table_widget.ImageTableWidget(self.root)
        self.open_windows.append(new_image_table)
