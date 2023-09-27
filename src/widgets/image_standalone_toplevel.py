import os
import tkinter as tk

from src.widgets import image_widget as iw


class StandaloneImage(tk.Toplevel):
    def __init__(self, parent, root, file_path, image_id):
        tk.Toplevel.__init__(self, root)

        file_name = os.path.basename(file_path)
        self.parent = parent
        self.root = root

        self.title(file_name)
        self.geometry("800x600")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.image_frame = iw.ImageFrame(self, self, file_path)
        self.image_id = image_id

        self.bind("<FocusIn>", self.handle_focus)

    def handle_focus(self, event):
        self.parent.set_selected_image(self.image_id)
        if self.root.widget_controller.open_windows["Render Configuration"] is not None:
            self.root.widget_controller.open_windows[
                "Render Configuration"
            ].update_selected_colour_map(self.image_frame.colour_map)
            self.root.update()
