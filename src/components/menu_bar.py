from functools import partial
from tkinter import filedialog

import ttkbootstrap as tb

from src.controllers import image_controller as ic
from src.controllers import widget_controller as wc


class MenuBar(tb.Frame):
    """The menu bar for the main window."""

    def __init__(self, root: tb.Window):
        """Construct a MenuBar.

        :param root: the main window
        """

        super().__init__(root)
        self.root = root
        self.grid(column=0, row=0)

        self.menu = tb.Menu(self.root)

        self.file_menu_creation()
        self.widget_menu_creation()

    def file_menu_creation(self):
        """Creates the File menu cascade"""

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
        """Creates the Widget menu cascade"""

        widget_menu = tb.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Widget", menu=widget_menu)

        # automatically construct the options from the Widget enum
        for widget in wc.Widget:
            if widget.value.dropdown is False:
                continue

            widget_menu.add_command(
                label=widget.value.label,
                command=partial(self.open_widget, widget),
            )

    def open_file(self):
        """Command for the Open Image option."""

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
        """Command for the Close Images option."""

        ic.close_images()

    def open_widget(self, widget: wc.Widget):
        """Command for all of the widget open options.

        :param widget: the widget to open
        """

        wc.open_widget(widget)
