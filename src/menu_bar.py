import platform
from functools import partial
from tkinter import filedialog
from typing import TYPE_CHECKING, Optional

import ttkbootstrap as tb

from src.enums import DataType
from src.widgets import widget_controller as wc
from src.widgets.image import image_controller as ic
from src.widgets.image.fits_handler import save_fits_file
from src.widgets.image.image_frame import ImageFrame

if TYPE_CHECKING:
    from src.main import MainWindow


class MenuBar(tb.Menu):
    """The menu bar for the main window."""

    def __init__(self, root: "MainWindow"):
        """Construct a MenuBar.

        :param root: the main window
        """

        super().__init__(root)
        self.root = root

        self.file_menu = tb.Menu(self, tearoff=False)  # , activeforeground="#BABABA")
        self.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open Image", command=self.open_file)
        self.file_menu.add_command(
            label="Open HiPs Survey",
            command=partial(self.open_widget, wc.Widget.HIPS_SELECT),
        )
        self.file_menu.add_command(label="Close All Images", command=self.close_images)

        self.file_menu.add_command(
            label="Save .hips as .fits",
            command=self.save_hips,
        )
        # the original state=disabled style is ugly
        self.hips_is_disabled = True
        self.update_hips_option()

        self.file_menu.add_command(label="Exit", command=self.root.quit)

        widget_menu = tb.Menu(self, tearoff=False)
        self.add_cascade(label="Widget", menu=widget_menu)

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

    def save_hips(self):
        if self.hips_is_disabled:
            # trying to emulate state=disabled, just re-open the menu lol
            self.file_menu.post(self.root.winfo_rootx(), self.root.winfo_rooty() - 1)
            return

        save_fits_file(
            self.root.main_image.image_data, self.root.main_image.image_data_header
        )

    def update_hips_option(self, selected_image: Optional["ImageFrame"] = None):
        if (
            selected_image is None
            or not selected_image.from_hips
            or selected_image.data_type != DataType.FITS
        ):
            self.hips_is_disabled = True

            foreground = "#BABABA"
            activeforeground = "#BABABA"
            background = "#2B3E50"
            activebackground = "#2B3E50"

            # looks fine on mac in the disabled state
            if platform.system() == "Darwin":
                self.file_menu.entryconfigure("Save .hips as .fits", state="disabled")
        else:
            self.hips_is_disabled = False

            foreground = self.file_menu.entrycget(0, "foreground")
            activeforeground = self.file_menu.entrycget(0, "activeforeground")
            background = self.file_menu.entrycget(0, "background")
            activebackground = self.file_menu.entrycget(0, "activebackground")

            # looks fine on mac in the disabled state
            if platform.system() == "Darwin":
                self.file_menu.entryconfigure("Save .hips as .fits", state="normal")

        self.file_menu.entryconfigure(
            "Save .hips as .fits",
            {
                "foreground": foreground,
                "activeforeground": activeforeground,
                "background": background,
                "activebackground": activebackground,
            },
        )

    def open_widget(self, widget: wc.Widget):
        """Command for all of the widget open options.

        :param widget: the widget to open
        """

        wc.open_widget(widget)
