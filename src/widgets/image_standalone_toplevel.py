import tkinter as tk
from functools import partial

from src import constants
from src.widgets import image_widget as iw


class StandaloneImage(tk.Toplevel):
    def __init__(
        self, parent, root, image_data, image_data_header, file_name, file_type
    ):
        super().__init__(root)

        self.title(file_name)
        self.geometry("800x600")
        self.iconbitmap(constants.FAVICON_PATH)  # windows title icon

        self.parent = parent
        self.root = root

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.dummy_frame = tk.Frame(self)
        self.dummy_frame.grid(column=0, row=0, sticky=tk.NSEW)
        self.dummy_frame.grid_rowconfigure(0, weight=1)
        self.dummy_frame.grid_columnconfigure(0, weight=1)

        self.image_frame = iw.ImageFrame(
            self.dummy_frame, root, image_data, image_data_header, file_name, file_type
        )

        self.bind("<FocusIn>", self.handle_focus)

        self.protocol(
            "WM_DELETE_WINDOW",
            partial(self.root.image_controller.close_appended_image, self),
        )

    def handle_focus(self, event):
        self.parent.set_selected_image(self)
