import re
import tkinter as tk
from functools import partial
from tkinter import messagebox

import numpy as np
import ttkbootstrap as tb

import src.controllers.image_controller as ic
import src.lib.contour_handler as contour_handler
from src.components.color_chooser import ColourChooserButton
from src.enums import DataType
from src.widgets.base_widget import BaseWidget

BAD_MEAN_SIGMA = 'One of the "Mean" or "Sigma" fields is invalid. They must be floats.'
BAD_LEVELS = (
    'The "Levels" field is invalid. It must be a comma separated list of numbers.'
)
BAD_LINEWIDTH_GAUSSIAN = 'One of the "Line Width" or "Gaussian Factor" fields is invalid. They must be floats.'
BAD_MEAN_SIGMA = "The Mean or Sigma field is invalid. They must be numbers"
BAD_LEVELS = (
    'The "Levels" field is invalid. It must be a comma separated list of numbers.'
)
BAD_SIGMAS = (
    'The "Sigma List" field is invalid. It must be a comma separated list of numbers.'
)
NOTHING_OPEN = "No image open"
NO_DATA_SOURCE = "No data source is loaded."
INVALID_IMAGE = "Cannot apply contours to png images."
INVALID_INPUT = "Invalid Input"


def validate_list_entry(text: str) -> bool:
    """Validates the given text matches the input for a "list" or "tag input"-like entry.

    Specifically to be used for sigma list and level fields.

    :param text: the text to validate
    """
    r = re.search(r"^(-?\d+(\.\d+|))(,-?\d+(\.\d+|))*$", text)
    return r is not None


class ContourWidget(BaseWidget):
    label = "Contours"
    dropdown = True

    def __init__(self, root):
        super().__init__(root)

        self.data_source = None
        self.line_opacity = 0.5

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frame = tb.Frame(self, bootstyle="light")
        self.frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
        self.frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.frame.grid_columnconfigure((0, 2), weight=1)
        self.frame.grid_columnconfigure((1, 3), weight=2)

        # Data Source
        data_source_frame = tb.Frame(self.frame, bootstyle="light")
        data_source_frame.grid(column=0, row=0, columnspan=4, padx=10, pady=10)

        data_source_label = tb.Label(
            data_source_frame, text="Data Source", bootstyle="inverse-light"
        )
        data_source_label.grid(column=0, row=0, padx=(0, 20))

        self.data_source_dropdown = tb.Menubutton(
            data_source_frame, text=NOTHING_OPEN, bootstyle="dark"
        )
        self.data_source_dropdown.grid(column=1, row=0)
        ic.update_image_list_eh.add(self.update_dropdown)

        # Parameters
        parameters_label = tb.Label(
            self.frame,
            text="Parameters",
            bootstyle="inverse-light",
            font=("Helvetica bold", 10),
        )
        parameters_label.grid(column=0, row=1, padx=10, pady=10, sticky=tk.W)

        mean_label = tb.Label(self.frame, text="Mean", bootstyle="inverse-light")
        mean_label.grid(column=0, row=2, padx=10, pady=10, sticky=tk.W)

        self.mean_entry = tb.Entry(self.frame)
        self.mean_entry.grid(column=1, row=2, padx=10, pady=10)

        sigma_label = tb.Label(self.frame, text="Sigma", bootstyle="inverse-light")
        sigma_label.grid(column=0, row=3, padx=10, pady=10, sticky=tk.W)

        self.sigma_entry = tb.Entry(self.frame)
        self.sigma_entry.grid(column=1, row=3, padx=10, pady=10)

        sigmas_label = tb.Label(
            self.frame, text="Sigma List", bootstyle="inverse-light"
        )
        sigmas_label.grid(column=0, row=4, padx=10, pady=10, sticky=tk.W)

        self.sigmas_entry = tb.Entry(self.frame)
        self.sigmas_entry.grid(column=1, row=4, padx=10, pady=10)

        # Generate Levels
        generate_button = tb.Button(
            self.frame,
            text="Generate",
            bootstyle="success",
            command=self.generate_levels,
        )
        generate_button.grid(column=1, row=5, padx=10, pady=(10, 20))

        # Levels
        levels_label = tb.Label(self.frame, text="Levels", bootstyle="inverse-light")
        levels_label.grid(column=0, row=6, padx=10, pady=10, sticky=tk.W)

        self.levels_entry = tb.Entry(self.frame)
        self.levels_entry.grid(column=1, row=6, padx=10, pady=10)

        # Apply / Close buttons
        self.buttons = tb.Frame(self.frame, bootstyle="light")
        self.buttons.grid(
            column=0, columnspan=4, row=7, sticky=tk.NSEW, padx=10, pady=10
        )
        self.buttons.rowconfigure(0, weight=1)
        self.buttons.columnconfigure(0, weight=1)

        self.clear_button = tb.Button(
            self.buttons,
            bootstyle="warning",
            text="Clear Selected",
            command=partial(self.clear_contours, selected=True),
        )
        self.clear_button.grid(column=0, row=0, sticky=tk.SE)

        self.apply_button = tb.Button(
            self.buttons,
            bootstyle="success",
            text="Apply Selected",
            command=partial(self.apply_contours, selected=True),
        )
        self.apply_button.grid(column=1, row=0, sticky=tk.SE, padx=10)

        self.clear_button = tb.Button(
            self.buttons,
            bootstyle="warning",
            text="Clear All",
            command=partial(self.clear_contours, selected=False),
        )
        self.clear_button.grid(column=2, row=0, sticky=tk.SE)

        self.apply_button = tb.Button(
            self.buttons,
            bootstyle="success",
            text="Apply All",
            command=partial(self.apply_contours, selected=False),
        )
        self.apply_button.grid(column=3, row=0, sticky=tk.SE, padx=10)

        self.close_button = tb.Button(
            self.buttons, bootstyle="danger-outline", text="Close", command=self.close
        )
        self.close_button.grid(column=4, row=0, sticky=tk.SE)

        # Configuration
        config_label = tb.Label(
            self.frame,
            text="Configuration",
            bootstyle="inverse-light",
            font=("Helvetica bold", 10),
        )
        config_label.grid(column=2, row=1, padx=10, pady=10, sticky=tk.W)

        gaussian_label = tb.Label(
            self.frame, text="Gaussian Factor", bootstyle="inverse-light"
        )
        gaussian_label.grid(column=2, row=2, padx=10, pady=10, sticky=tk.W)

        self.gaussian_entry = tb.Entry(self.frame)
        self.gaussian_entry.grid(column=3, row=2, padx=10, pady=10, sticky=tk.W)
        self.gaussian_entry.insert(0, "4")

        # Styling
        styling_label = tb.Label(
            self.frame,
            text="Styling",
            bootstyle="inverse-light",
            font=("Helvetica bold", 10),
        )
        styling_label.grid(column=2, row=3, padx=10, pady=10, sticky=tk.W)

        lc_label = tb.Label(self.frame, text="Line Colour", bootstyle="inverse-light")
        lc_label.grid(column=2, row=4, padx=10, pady=10, sticky=tk.W)

        self.lc_button = ColourChooserButton(
            self.frame, width=24, height=24, window_title="Choose Contour Line Colour"
        )
        self.lc_button.grid(column=3, row=4, sticky=tk.W, padx=10)

        self.lo_label = tb.Label(
            self.frame, text="Line Opacity (0.50)", bootstyle="inverse-light"
        )
        self.lo_label.grid(column=2, row=5, padx=10, pady=10, sticky=tk.W)

        self.lo_slider = tb.Scale(
            self.frame, command=self.set_line_opacity, value=self.line_opacity
        )
        self.lo_slider.grid(column=3, row=5, padx=10, pady=10, sticky=tk.W)

        self.lw_label = tb.Label(
            self.frame, text="Line Width", bootstyle="inverse-light"
        )
        self.lw_label.grid(column=2, row=6, padx=10, pady=10, sticky=tk.W)

        self.lw_entry = tb.Entry(self.frame)
        self.lw_entry.insert(0, 0.5)
        self.lw_entry.grid(column=3, row=6, padx=10, pady=10, sticky=tk.W)

        self.update_dropdown(
            ic.get_selected_image(),
            ic.get_images(),
        )

    @property
    def line_colour(self) -> str:
        """The currently selected line_colour."""
        return self.lc_button.get()

    def get_data_source(self):
        return self.data_source

    def set_data_source(self, image):
        # clear inputs
        self.mean_entry.delete(0, tk.END)
        self.sigma_entry.delete(0, tk.END)
        self.sigmas_entry.delete(0, tk.END)
        self.levels_entry.delete(0, tk.END)

        if image is None or image.data_type != DataType.FITS:
            self.data_source = None
            self.data_source_dropdown["text"] = NOTHING_OPEN
            return

        self.data_source = image
        self.data_source_dropdown["text"] = image.file_name

        # TODO Potentially remember these between data sources so that you don't lose information?
        # TODO I guess I'm more curious what behaviour we expect here. CARTA maintains it when switching
        self.mean_entry.insert(0, str(np.nanmean(self.data_source.image_data)))
        self.sigma_entry.insert(
            0, str(contour_handler.get_sigma(self.data_source.image_data))
        )
        # TODO better default? this is the default from carta
        self.sigmas_entry.insert(0, "-5,5,9,13,17")
        self.generate_levels()

    def update_dropdown(self, selected_image, image_list):
        # Always change the commands to match the current list
        self.data_source_menu = tk.Menu(self.data_source_dropdown, tearoff=0)
        self.data_source_dropdown["menu"] = self.data_source_menu

        selected_still_open = False
        for image in image_list:
            if image.image_wcs is None:
                continue

            self.data_source_menu.add_command(
                label=image.file_name,
                command=partial(self.set_data_source, image),
            )

            if image == self.data_source:
                selected_still_open = True

        if len(image_list) == 0:
            # If the image list is empty, default text in the dropdown
            self.set_data_source(None)
        elif not selected_still_open or self.get_data_source() is None:
            # Otherwise if the selected image was closed
            #   or we previously had nothing selected,
            #   pick the new selected
            self.set_data_source(selected_image)

    def generate_levels(self):
        """
        We clicked "Generate".
        """

        if self.get_data_source() is None:
            messagebox.showerror(title=INVALID_INPUT, message=NO_DATA_SOURCE)
            return

        try:
            mean = float(self.mean_entry.get())
            sigma = float(self.sigma_entry.get())
        except ValueError:
            messagebox.showerror(title=INVALID_INPUT, message=BAD_MEAN_SIGMA)
            return

        sigma_list = self.sigmas_entry.get().strip()

        # if the user input is bad spit out a warning and exit early
        if not validate_list_entry(sigma_list):
            messagebox.showerror(title=INVALID_INPUT, message=BAD_SIGMAS)
            return

        sigma_list = [float(x) for x in sigma_list.split(",")]

        levels = contour_handler.generate_levels(mean, sigma, sigma_list)
        self.levels_entry.delete(0, tk.END)
        self.levels_entry.insert(0, ",".join(str(x) for x in levels))

    def apply_contours(self, selected):
        """
        We clicked "Apply".
        """

        if self.get_data_source() is None:
            messagebox.showerror(title=INVALID_INPUT, message=NO_DATA_SOURCE)
            return

        try:
            line_width = float(self.lw_entry.get())
            gaussian_factor = float(self.gaussian_entry.get())
        except ValueError:
            messagebox.showerror(
                title=INVALID_INPUT,
                message=BAD_LINEWIDTH_GAUSSIAN,
            )
            return

        input = self.levels_entry.get().strip()

        # if the user input is bad spit out a warning and exit early
        if not validate_list_entry(input):
            messagebox.showerror(
                title=INVALID_INPUT,
                message=BAD_LEVELS,
            )
            return

        images = ic.get_images() if not selected else [ic.get_selected_image()]

        for image in images:
            if image is None or image.data_type != DataType.FITS:
                if selected:
                    messagebox.showerror(title=INVALID_INPUT, message=INVALID_IMAGE)
                    return
                continue

            image.update_contours(
                self.data_source.image_data,
                self.data_source.image_wcs,
                [float(x) for x in input.split(",")],
                gaussian_factor,
                self.line_colour,
                self.line_opacity,
                line_width,
            )

    def clear_contours(self, selected):
        images = ic.get_images() if not selected else [ic.get_selected_image()]

        for image in images:
            image.clear_contours()

    def set_line_opacity(self, value):
        value = float(value)
        self.line_opacity = value
        self.lo_label["text"] = f"Line Opacity ({value:1.2f})"

    def close(self):
        ic.update_image_list_eh.remove(self.update_dropdown)
        super().close()
