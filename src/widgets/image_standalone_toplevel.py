import tkinter as tk

from src.widgets import image_widget as iw


class StandaloneImage(tk.Toplevel):
    def __init__(
        self, parent, root, image_data, image_data_header, file_name, image_id
    ):
        tk.Toplevel.__init__(self, root)

        self.parent = parent
        self.root = root

        self.title(file_name)
        self.geometry("800x600")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.image_frame = iw.ImageFrame(
            self, self, image_data, image_data_header, file_name
        )
        self.image_id = image_id

        self.bind("<FocusIn>", self.handle_focus)

    def handle_focus(self, event):
        self.parent.set_selected_image(self.image_id)

        if self.root.widget_controller.open_windows["Render Configuration"] is None:
            return

        self.root.widget_controller.open_windows[
            "Render Configuration"
        ].update_selected_scaling(self.image_frame.stretch)

        self.root.widget_controller.open_windows[
            "Render Configuration"
        ].update_selected_colour_map(self.image_frame.colour_map)

        self.root.update()
