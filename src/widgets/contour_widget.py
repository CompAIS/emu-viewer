import re
import tkinter as tk
from functools import partial
from tkinter import messagebox

import numpy as np
import ttkbootstrap as tb

from src.lib import contour_handler
from src.widgets.base_widget import BaseWidget

BAD_MEAN_SIGMA = "The Mean or Sigma field is invalid. They must be numbers"
BAD_LEVELS = (
    'The "Levels" field is invalid. It must be a comma separated list of numbers.'
)
BAD_SIGMAS = (
    'The "Sigma List" field is invalid. It must be a comma separated list of numbers.'
)
NOTHING_OPEN = "No image open"
NO_DATA_SOURCE = "No data source is loaded."
INVALID_INPUT = "Invalid Input"


def validate_list_entry(text):
    """
    Validates the given text matches the input for a "list" or "tag input"-like entry.

    Specifically to be used for sigma list and level fields.
    """
    r = re.search(r"^(-?\d+(\.\d+|))(,-?\d+(\.\d+|))*$", text)
    return r is not None


class ContourWidget(BaseWidget):
    label = "Contours"
    dropdown = True

    def __init__(self, root):
        super().__init__(root)

        self.data_source = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frame = tb.Frame(self, bootstyle="light")
        self.frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
        self.frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=2)

        # Data Source
        data_source_label = tb.Label(
            self.frame, text="Data Source", bootstyle="inverse-light"
        )
        data_source_label.grid(column=0, row=0, padx=10, pady=10, sticky=tk.W)

        self.data_source_dropdown = tb.Menubutton(
            self.frame, text=NOTHING_OPEN, bootstyle="dark"
        )
        self.data_source_dropdown.grid(column=1, row=0, padx=10, pady=10)
        self.root.image_controller.update_image_list_eh.add(self.update_dropdown)

        parameters_label = tb.Label(
            self.frame,
            text="Parameters",
            bootstyle="inverse-light",
            font=("Helvetica bold", 10),
        )
        parameters_label.grid(column=0, row=1, padx=10, pady=10, sticky=tk.W)

        # Parameters
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
        generate_button.grid(column=0, row=5, columnspan=2, padx=10, pady=(10, 20))

        # Levels
        levels_label = tb.Label(self.frame, text="Levels", bootstyle="inverse-light")
        levels_label.grid(column=0, row=6, padx=10, pady=10, sticky=tk.W)

        self.levels_entry = tb.Entry(self.frame)
        self.levels_entry.grid(column=1, columnspan=2, row=6, padx=10, pady=10)

        # Apply / Close buttons
        self.buttons = tb.Frame(self.frame, bootstyle="light")
        self.buttons.grid(column=1, row=7, sticky=tk.NSEW, padx=10, pady=10)
        self.buttons.rowconfigure(0, weight=1)
        self.buttons.columnconfigure(0, weight=1)

        self.clear_button = tb.Button(
            self.buttons, bootstyle="warning", text="Clear", command=self.clear_contours
        )
        self.clear_button.grid(column=0, row=0, sticky=tk.SE)

        self.apply_button = tb.Button(
            self.buttons, bootstyle="success", text="Apply", command=self.apply_contours
        )
        self.apply_button.grid(column=1, row=0, sticky=tk.SE, padx=10)

        self.close_button = tb.Button(
            self.buttons, bootstyle="danger-outline", text="Close", command=self.close
        )
        self.close_button.grid(column=2, row=0, sticky=tk.SE)

        self.update_dropdown(
            self.root.image_controller.get_selected_image(),
            self.root.image_controller.get_images(),
        )

    def get_data_source(self):
        return self.data_source

    def set_data_source(self, image):
        # clear inputs
        self.mean_entry.delete(0, tk.END)
        self.sigma_entry.delete(0, tk.END)
        self.sigmas_entry.delete(0, tk.END)
        self.levels_entry.delete(0, tk.END)

        if image is None:
            self.data_source = None
            self.data_source_dropdown["text"] = NOTHING_OPEN
            return

        self.data_source = image
        self.data_source_dropdown["text"] = image.file_name

        # TODO Potentially remember these between data sources so that you don't lose information?
        # TODO I guess I'm more curious what behaviour we expect here. CARTA maintains it when switching
        self.mean_entry.insert(0, str(np.nanmean(self.data_source.image_data)))
        self.sigma_entry.insert(0, str(np.nanstd(self.data_source.image_data)))
        # TODO better default? this is the default from carta
        self.sigmas_entry.insert(0, "-5,5,9,13,17")
        self.generate_levels()

    def update_dropdown(self, selected_image, image_list):
        # Always change the commands to match the current list
        self.data_source_menu = tk.Menu(self.data_source_dropdown, tearoff=0)
        self.data_source_dropdown["menu"] = self.data_source_menu

        selected_still_open = False
        for image in image_list:
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

    def apply_contours(self):
        """
        We clicked "Apply".
        """

        if self.get_data_source() is None:
            messagebox.showerror(title=INVALID_INPUT, message=NO_DATA_SOURCE)
            return

        input = self.levels_entry.get().strip()

        # if the user input is bad spit out a warning and exit early
        if not validate_list_entry(input):
            messagebox.showerror(
                title=INVALID_INPUT,
                message=BAD_LEVELS,
            )
            return

        self.data_source.update_contours([float(x) for x in input.split(",")])

    def clear_contours(self):
        self.root.image_controller.get_selected_image().update_contours(None)
