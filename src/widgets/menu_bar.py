from functools import partial
from tkinter import filedialog

import ttkbootstrap as tb

import src.controllers.image_controller as ic
import src.controllers.widget_controller as wc
from src.lib.event_handler import EventHandler
from src.widgets.hips_selector_widget import HipsSelectorWidget


# Create Menu bar for tkinter window
class MenuBar(tb.Frame):
    open_widget_eh = EventHandler()

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

    def open_hips(self):
        hips_selector = HipsSelectorWidget(self.root)
        self.root.wait_window(hips_selector)

        hips_survey = hips_selector.hips_survey
        wcs = hips_selector.selected_wcs

        if (
            hips_survey.projection == ""
            or hips_survey.survey == ""
            or hips_survey.data_type is None
        ):
            return

        ic.open_hips(hips_survey, wcs)

    def close_images(self):
        ic.close_images()

    def open_widget(self, widget):
        self.open_widget_eh.invoke(widget)
