import tkinter as tk
from functools import partial

import src.controllers.image_controller as ic
from src import constants
from src.enums import DataType
from src.widgets import image_widget as iw


class StandaloneImage(tk.Toplevel):
    def __init__(
        self, root, image_data, image_data_header, file_name, data_type: DataType
    ):
        super().__init__(root)

        self.title(file_name)
        self.geometry("800x600")
        self.iconbitmap(constants.FAVICON_PATH)  # windows title icon

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.dummy_frame = tk.Frame(self)
        self.dummy_frame.grid(column=0, row=0, sticky=tk.NSEW)
        self.dummy_frame.grid_rowconfigure(0, weight=1)
        self.dummy_frame.grid_columnconfigure(0, weight=1)

        self.image_frame = iw.ImageFrame(
            self.dummy_frame, root, image_data, image_data_header, file_name, data_type
        )

        self.bind("<FocusIn>", self.handle_focus)

        self.protocol("WM_DELETE_WINDOW", partial(ic.close_standalone, self))

    def handle_focus(self, event):
        ic.set_selected_image(self.image_frame)
