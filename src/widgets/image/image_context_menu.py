import tkinter as tk
from typing import TYPE_CHECKING

import src.widgets.widget_controller as wc

if TYPE_CHECKING:
    from src.widgets.image.image_frame import ImageFrame


class ImageContextMenu(tk.Menu):
    """The context memnu that appears when you right click the image."""

    def __init__(
        self, image_frame: "ImageFrame", xdata: float, ydata: float, value: float
    ):
        """Construct an ImageContextMenu.

        :param image_frame: the image frame this context menu is for
        :param xdata: the x position of the cursor relative to the image_data
        :param ydata: the y position of the cursor relative to the image_data
        :param value: the value of the point where the cursor is
        """

        super().__init__(image_frame, tearoff=0)
        self.image_frame = image_frame
        self.xdata = xdata
        self.ydata = ydata
        self.coord = image_frame.image_wcs.pixel_to_world(xdata, ydata)
        self.value = value

        self.add_command(
            label="Copy WCS Coords (Decimal)", command=self.copy_decimal_coords
        )
        self.add_command(
            label="Copy WCS Coords (HMSDMS)", command=self.copy_hmsdms_coords
        )
        self.add_command(label="Copy Image Coords", command=self.copy_image_coords)
        self.add_command(label="Copy Value at Coords", command=self.copy_coord_value)
        self.add_separator()
        self.add_command(
            label="Set RA/DEC in HiPs Survey Selector", command=self.set_ra_dec
        )

    def copy_decimal_coords(self):
        decimal = self.coord.to_string(style="decimal").replace(" ", ", ")
        self.copy_to_clipboard(f"WCS: ({decimal})")

    def copy_hmsdms_coords(self):
        hmsdms = self.coord.to_string(style="hmsdms", sep=":", pad=True).replace(
            " ", ", "
        )
        self.copy_to_clipboard(f"WCS: ({hmsdms})")

    def copy_image_coords(self):
        self.copy_to_clipboard(f"Image: ({self.xdata}, {self.ydata})")

    def copy_coord_value(self):
        self.copy_to_clipboard(str(self.value))

    def copy_to_clipboard(self, text):
        """Copy text to the clipboard.

        :param text: what to copy
        """
        self.image_frame.clipboard_clear()
        self.image_frame.clipboard_append(text)
        self.image_frame.update()

    def set_ra_dec(self):
        wc.open_widget(wc.Widget.HIPS_SELECT)

        decimal = self.coord.to_string(style="decimal")
        coords = decimal.split()
        wc.get_widget(wc.Widget.HIPS_SELECT).set_ra_dec_entries(coords[0], coords[1])
