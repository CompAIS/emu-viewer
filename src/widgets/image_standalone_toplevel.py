import tkinter as tk
from functools import partial

from src.widgets import image_widget as iw
from src.widgets import tool_bar as tool_bar


class StandaloneImage(tk.Toplevel):
    def __init__(
        self, parent, root, image_data, image_data_header, file_name, image_id
    ):
        tk.Toplevel.__init__(self, root)

        self.parent = parent
        self.root = root
        self.image_id = image_id

        self.title(file_name)
        self.geometry("800x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.toolbar = tool_bar.ToolBar(self)

        self.dummy_frame = tk.Frame(self)
        self.dummy_frame.grid(column=1, row=0, sticky=tk.NSEW)
        self.dummy_frame.grid_rowconfigure(0, weight=1)
        self.dummy_frame.grid_columnconfigure(0, weight=1)

        self.image_frame = iw.ImageFrame(
            self.dummy_frame, root, image_data, image_data_header, file_name
        )

        self.bind("<FocusIn>", self.handle_focus)

        self.protocol(
            "WM_DELETE_WINDOW",
            partial(self.root.image_controller.close_appended_image, self),
        )

    def handle_focus(self, event):
        self.parent.set_selected_image(self.image_id)
