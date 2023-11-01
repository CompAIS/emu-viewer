import platform
import tkinter as tk
from functools import partial
from typing import TYPE_CHECKING, Optional

import numpy.typing as npt

import src.widgets.image.image_controller as ic
from src import constants
from src.enums import DataType
from src.widgets.image import image_frame
from src.widgets.image.image_standalone_menubar import StandaloneImageMenuBar

if TYPE_CHECKING:
    from astropy.io import fits

    from src.main import MainWindow


class StandaloneImage(tk.Toplevel):
    """A separate window for any images opened after one is already open.

    Just wraps an ImageFrame under a tk.Toplevel with a menu bar
    """

    def __init__(
        self,
        root: "MainWindow",
        image_data: npt.ArrayLike,
        image_data_header: Optional["fits.Header"],
        file_name: str,
        data_type: DataType,
        from_hips: bool,
    ):
        """Construct a StandaloneImage.

        :param root: the root of the application (the main window).
        :param image_data: numpy array with the image's data (fits image or png image). Note that this should
            be float[][].
        :param image_data_header: HDU header for the .fits file. None for png/jpg.
        :param file_name: the name of the file where the data came from. HiPs survey name for hips
        :param data_type: the type of the data in image_data.
        :param from_hips: if the data came from a HiPs survey
        """

        super().__init__(root)

        self.title(file_name)
        self.geometry("800x600")

        if platform.system() == "Linux":
            self.iconphoto(True, constants.FAVICON)
        else:
            self.iconbitmap(constants.FAVICON)  # windows title icon

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.dummy_frame = tk.Frame(self)
        self.dummy_frame.grid(column=0, row=0, sticky=tk.NSEW)
        self.dummy_frame.grid_rowconfigure(0, weight=1)
        self.dummy_frame.grid_columnconfigure(0, weight=1)

        self.image_frame = image_frame.ImageFrame(
            self.dummy_frame,
            root,
            image_data,
            image_data_header,
            file_name,
            data_type,
            from_hips,
        )

        self.menu = StandaloneImageMenuBar(self)
        self.config(menu=self.menu)

        self.bind("<FocusIn>", self.handle_focus)
        self.protocol("WM_DELETE_WINDOW", partial(ic.close_standalone, self))

    def handle_focus(self, event):
        ic.set_selected_image(self.image_frame)
