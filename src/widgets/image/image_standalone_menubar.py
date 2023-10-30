import platform
from typing import TYPE_CHECKING

import ttkbootstrap as tb

from src.enums import DataType
from src.widgets.image import image_controller as ic
from src.widgets.image.fits_handler import save_fits_file

if TYPE_CHECKING:
    from src.widgets.image.image_standalone_toplevel import StandaloneImage


class StandaloneImageMenuBar(tb.Menu):
    """The menu bar for the standalone images."""

    def __init__(self, root: "StandaloneImage"):
        """Construct a StandaloneImageMenuBar.

        :param root: the standalone image
        """

        super().__init__(root, tearoff=False)
        self.root = root

        self.file_menu = tb.Menu(
            self,
            tearoff=False,
            disabledforeground="#BABABA",
            activeforeground="#BABABA",
            background="#BABABA",
        )
        self.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(
            label="Save .hips as .fits",
            command=self.save_hips,
        )

        # looks fine on mac
        if platform.system() == "Darwin":
            self.file_menu.entryconfigure("Save .hips as .fits", state="disabled")

        self.hips_is_disabled = (
            not self.root.image_frame.from_hips
            or self.root.image_frame.data_type != DataType.FITS
        )

        if self.hips_is_disabled:
            self.file_menu.entryconfig(
                "Save .hips as .fits",
                foreground="#BABABA",
                activeforeground="#BABABA",
                background="#2B3E50",
                activebackground="#2B3E50",
            )

        self.file_menu.add_command(label="Close Image", command=self.close_image)

    def save_hips(self):
        if self.hips_is_disabled:
            # trying to emulate state=disabled, just re-open the menu lol
            self.file_menu.post(self.root.winfo_rootx(), self.root.winfo_rooty() - 1)
            return

        save_fits_file(
            self.root.image_frame.image_data, self.root.image_frame.image_data_header
        )

    def close_image(self):
        ic.close_standalone(self.root)
