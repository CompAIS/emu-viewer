from functools import partial
from tkinter import filedialog

import ttkbootstrap as tb

from src.controllers.widget_controller import Widget
from src.lib.event_handler import EventHandler
from src.widgets.hips_selector_widget import HipsSelectorWidget


# Create Menu bar for tkinter window
class MenuBar(tb.Frame):
    open_fits_eh = EventHandler()
    open_png_eh = EventHandler()
    open_hips_eh = EventHandler()
    close_images_eh = EventHandler()
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
        file_menu.add_command(label="Open Hips Survey", command=self.open_hips)
        file_menu.add_command(label="Close All Images", command=self.close_images)
        file_menu.add_command(label="Exit", command=self.root.quit)

    def widget_menu_creation(self):
        widget_menu = tb.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Widget", menu=widget_menu)

        for widget in Widget:
            if widget.value.dropdown is False:
                continue

            widget_menu.add_command(
                label=widget.value.label,
                command=partial(self.open_widget, widget),
            )

    # Open command for option in menu
    def open_file(self):
        file_name = filedialog.askopenfilename(
            title="Select file",
            filetypes=(
                ("Fits/Png files", "*.fits *.png"),
                ("All files", "*.*"),
            ),
        )

        if file_name == "":
            return

        if file_name.endswith("fits"):
            self.open_fits_eh.invoke(file_name)
        elif file_name.endswith("png"):
            self.open_png_eh.invoke(file_name)

    def open_hips(self):
        hips_selector = HipsSelectorWidget(self.root)
        self.root.wait_window(hips_selector)

        hips_survey = hips_selector.hips_survey
        wcs = hips_selector.selected_wcs

        if (
            hips_survey.projection == ""
            or hips_survey.survey == ""
            or hips_survey.image_type == ""
        ):
            return

        self.open_hips_eh.invoke(hips_survey, wcs)

    def close_images(self):
        self.close_images_eh.invoke()

    def open_widget(self, widget):
        self.open_widget_eh.invoke(widget)
