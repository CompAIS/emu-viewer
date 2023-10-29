from functools import partial
from tkinter import filedialog

import ttkbootstrap as tb

from src.controllers import image_controller as ic
from src.controllers import widget_controller as wc


# Create Menu bar for tkinter window
class MenuBar(tb.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.grid(column=0, row=0)

        self.menu = tb.Menu(self.root)

        self.file_menu_creation()
        self.widget_menu_creation()

    # Create file menu options
    def file_menu_creation(self):
        file_menu = tb.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.open_file)
        file_menu.add_command(
            label="Open Hips Survey",
            command=partial(self.open_widget, wc.Widget.HIPS_SELECT),
        )
        file_menu.add_command(label="Close All Images", command=self.close_images)
        file_menu.add_command(label="Exit", command=self.root.quit)

    def widget_menu_creation(self):
        widget_menu = tb.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Widget", menu=widget_menu)

        for widget in wc.Widget:
            if widget.value.dropdown is False:
                continue

            widget_menu.add_command(
                label=widget.value.label,
                command=partial(self.open_widget, widget),
            )

    # Open command for option in menu
    def open_file(self):
        file_name = filedialog.askopenfilename(
            title="Select file to open",
            filetypes=(
                ("valid image files", "*.fits *.png"),
                ("All files", "*.*"),
            ),
        )

        if file_name == "":
            return

        if file_name.endswith("fits"):
            ic.open_fits(file_name)
        elif file_name.endswith("png"):
            ic.open_png(file_name)

    def close_images(self):
        ic.close_images()

    def open_widget(self, widget: wc.Widget):
        wc.open_widget(widget)
