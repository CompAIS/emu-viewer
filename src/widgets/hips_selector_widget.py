import tkinter as tk
from functools import partial
from tkinter import messagebox

import ttkbootstrap as tb

from src.lib.hips_handler import HipsSurvey
from src.widgets.base_widget import BaseWidget

projection_options = ["TAN", "ARC", "AIT"]

optical_survey_options = [
    "CDS/P/Skymapper-color-IRG",
    "CDS/P/skymapper-R",
    "CDS/P/DSS2/color",
    "CDS/P/DSS2/red",
    "CDS/P/DES-DR2/ColorIRG",
    "CDS/P/DES-DR2/r",
    "CDS/P/DESI-Legacy-Surveys/DR10/color",
    "CDS/P/DESI-Legacy-Surveys/DR10/r",
    "CDS/P/DM/flux-Bp/I/355/gaiadr3",
]

infrared_survey_options = [
    "CDS/P/unWISE/W1",
]

radio_survey_options = [
    "CSIRO/P/RACS/low/I",
    "CSIRO/P/RACS/mid/I",
    "CDS/P/HI4PI/NHI",
]

xray_survey_options = ["ov-gso/P/RASS"]

image_type_options = ["fits", "png", "jpg"]

NO_IMAGE_SELECTED = "No Image Selected"
NO_PROJECTION_SELECTED = "No Projection Selected"
NO_SURVEY_SELECTED = "No Survey Selected"
NO_IMAGE_TYPE_SELECTED = "No Image Type Selected"

INVALID_INPUT = "Invalid Input"
INVALID_RA = "Invalid RA, please enter a float"
INVALID_DEC = "Invalid Dec, please enter a float"
INVALID_FOV = "Invalid FOV, please enter a float"
INVALID_FOV_LOW = "Invalid FOV, FOV must be greater then 0"
ERROR_GENERATING = "Error generating image, either incorrect survey has been entered or selected image is to large"

COL_WIDTHS = [37, 23]


class HipsSelectorWidget(BaseWidget):
    label = "Hips Survey Selector"
    dropdown = False

    def __init__(self, root):
        super().__init__(root)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.selected_projection = None
        self.selected_hips_survey = None
        self.selected_image_type = None
        self.selected_wcs = None

        self.hips_survey = HipsSurvey()

        self.setup()

        self.root.image_controller.update_image_list_eh.add(self.update_valid_images)

    def setup(self):
        frame = tb.Frame(self, bootstyle="light")
        frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        frame.columnconfigure((0, 1, 2, 3), weight=1)
        frame.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.optical_dropdown = self.dropdown_options(
            frame,
            "Optical Hips Surveys",
            NO_SURVEY_SELECTED,
            optical_survey_options,
            self.select_survey_option,
            COL_WIDTHS[0],
            0,
            0,
        )

        self.infrared_dropdown = self.dropdown_options(
            frame,
            "Infrared Hips Surveys",
            NO_SURVEY_SELECTED,
            infrared_survey_options,
            self.select_survey_option,
            COL_WIDTHS[0],
            0,
            1,
        )

        self.radio_dropdown = self.dropdown_options(
            frame,
            "Radio Hips Surveys",
            NO_SURVEY_SELECTED,
            radio_survey_options,
            self.select_survey_option,
            COL_WIDTHS[0],
            0,
            2,
        )

        self.xray_dropdown = self.dropdown_options(
            frame,
            "X-Ray Hips Surveys",
            NO_SURVEY_SELECTED,
            xray_survey_options,
            self.select_survey_option,
            COL_WIDTHS[0],
            0,
            3,
        )

        self.custom_survey = self.entry_options(frame, "Custom Survey", 0, 4)
        self.custom_survey.bind("<FocusOut>", self.custom_survey_focusout)

        self.image_type_dropdown = self.dropdown_options(
            frame,
            "Image Type",
            NO_IMAGE_TYPE_SELECTED,
            image_type_options,
            self.select_image_type,
            COL_WIDTHS[0],
            0,
            5,
        )

        image_select_label = tb.Label(
            frame, text="Open Images", bootstyle="inverse-light"
        )
        image_select_label.grid(column=2, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.image_select_dropdown = tb.Menubutton(
            frame, text=NO_IMAGE_SELECTED, width=COL_WIDTHS[1], bootstyle="dark"
        )
        self.image_select_dropdown.grid(column=3, row=0, sticky=tk.EW, padx=10, pady=10)

        self.update_valid_images(None, self.root.image_controller.get_images())

        self.ra_entry = self.entry_options(frame, "RA", 2, 1)

        self.dec_entry = self.entry_options(frame, "Dec", 2, 2)

        self.FOV_entry = self.entry_options(frame, "FOV", 2, 3)

        self.projection_dropdown = self.dropdown_options(
            frame,
            "Projection",
            NO_PROJECTION_SELECTED,
            projection_options,
            self.select_projection,
            COL_WIDTHS[1],
            2,
            4,
        )

        button_frame = tb.Frame(frame, bootstyle="light")
        button_frame.grid(column=2, columnspan=2, row=5, sticky=tk.NSEW)

        button_frame.columnconfigure((0, 1), weight=1)
        button_frame.rowconfigure(0, weight=1)

        self.custom_button(
            button_frame, "Reset", "warning", self.reset_all_options, 0, 0
        )
        self.custom_button(
            button_frame, "Select Survey", "success", self.select_survey, 1, 0
        )

    def dropdown_options(
        self, parent, text, dropdown_text, options, func, width, gridX, gridY
    ):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown = tb.Menubutton(
            parent, text=dropdown_text, width=width, bootstyle="dark"
        )
        dropdown.grid(column=gridX + 1, row=gridY, sticky=tk.EW, padx=10, pady=10)
        dropdown_menu = tk.Menu(dropdown, tearoff=0)

        for option in options:
            dropdown_menu.add_command(
                label=option,
                command=partial(func, option, dropdown),
            )

        dropdown["menu"] = dropdown_menu

        return dropdown

    def select_projection(self, projection, dropdown):
        self.selected_projection = projection
        dropdown["text"] = projection

    def select_survey_option(self, hips_survey, dropdown):
        self.clear_survey_options()
        self.selected_hips_survey = hips_survey
        dropdown["text"] = hips_survey

    def clear_survey_options(self):
        self.optical_dropdown["text"] = NO_SURVEY_SELECTED
        self.infrared_dropdown["text"] = NO_SURVEY_SELECTED
        self.radio_dropdown["text"] = NO_SURVEY_SELECTED
        self.xray_dropdown["text"] = NO_SURVEY_SELECTED
        self.custom_survey.delete(0, tk.END)

    def select_image_type(self, image_type, dropdown):
        self.selected_image_type = image_type
        dropdown["text"] = image_type

    def select_image(self, image, dropdown):
        if image is None:
            self.selected_wcs = None
            dropdown["text"] = NO_IMAGE_SELECTED
            self.ra_entry.configure(state="enabled")
            self.dec_entry.configure(state="enabled")
            self.FOV_entry.configure(state="enabled")
        else:
            self.selected_wcs = image.image_wcs
            dropdown["text"] = image.file_name
            self.ra_entry.configure(state="disabled")
            self.dec_entry.configure(state="disabled")
            self.FOV_entry.configure(state="disabled")

    def entry_options(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        entry = tb.Entry(parent, bootstyle="dark")
        entry.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        return entry

    def custom_survey_focusout(self, event):
        self.custom_survey_enter()

    def custom_survey_enter(self):
        if self.custom_survey.get() == "":
            return

        self.selected_hips_survey = self.custom_survey.get()
        self.optical_dropdown["text"] = NO_SURVEY_SELECTED
        self.infrared_dropdown["text"] = NO_SURVEY_SELECTED
        self.radio_dropdown["text"] = NO_SURVEY_SELECTED
        self.xray_dropdown["text"] = NO_SURVEY_SELECTED

    def custom_button(self, parent, text, style, func, gridX, gridY):
        button = tb.Button(
            parent,
            text=text,
            bootstyle=style,
            command=partial(func),
        )
        button.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

    def reset_all_options(self):
        self.selected_projection = None
        self.selected_hips_survey = None
        self.selected_image_type = None
        self.selected_wcs = None

        self.clear_survey_options()
        self.image_type_dropdown["text"] = NO_IMAGE_TYPE_SELECTED

        self.image_select_dropdown["text"] = NO_IMAGE_SELECTED
        self.ra_entry.delete(0, tk.END)
        self.dec_entry.delete(0, tk.END)
        self.FOV_entry.delete(0, tk.END)
        self.projection_dropdown["text"] = NO_PROJECTION_SELECTED

    def select_survey(self):
        self.custom_survey_enter()

        if (
            self.selected_projection is None
            or self.selected_hips_survey is None
            or self.selected_image_type is None
        ):
            return

        self.hips_survey.projection = self.selected_projection
        self.hips_survey.survey = self.selected_hips_survey
        self.hips_survey.image_type = self.selected_image_type

        if self.selected_wcs is None:
            self.hips_survey.ra = self.float_validation(self.ra_entry, INVALID_RA)
            self.hips_survey.dec = self.float_validation(self.dec_entry, INVALID_DEC)
            self.hips_survey.FOV = self.float_validation(self.FOV_entry, INVALID_FOV)

            if self.hips_survey.FOV <= 0:
                self.hips_survey.FOV = "F"
                messagebox.showerror(
                    title=INVALID_INPUT,
                    message=INVALID_FOV_LOW,
                )

        if (
            self.hips_survey.ra == "F"
            or self.hips_survey.dec == "F"
            or self.hips_survey.FOV == "F"
        ):
            return

        try:
            self.root.image_controller.open_hips(self.hips_survey, self.selected_wcs)
        except AttributeError:
            messagebox.showerror(
                title="Error",
                message=ERROR_GENERATING,
            )
            return

        # Not sure if this is wanted or not
        # self.reset_all_options()

    def float_validation(self, entry, error):
        try:
            valid_float = float(entry.get())
        except ValueError:
            messagebox.showerror(
                title=INVALID_INPUT,
                message=error,
            )
            return "F"

        return valid_float

    def update_valid_images(self, selected_image, image_list):
        if selected_image is None:
            self.image_select_dropdown["text"] = NO_IMAGE_SELECTED

        valid_images = [image for image in image_list if image.image_wcs is not None]

        dropdown_menu = tk.Menu(self.image_select_dropdown, tearoff=0)

        dropdown_menu.add_command(
            label=NO_IMAGE_SELECTED,
            command=partial(self.select_image, None, self.image_select_dropdown),
        )

        for option in valid_images:
            dropdown_menu.add_command(
                label=option.file_name,
                command=partial(self.select_image, option, self.image_select_dropdown),
            )

        self.image_select_dropdown["menu"] = dropdown_menu

    def set_ra_dec_entries(self, ra, dec):
        self.ra_entry.delete(0, tk.END)
        self.ra_entry.insert(0, ra)
        self.dec_entry.delete(0, tk.END)
        self.dec_entry.insert(0, dec)

    def close(self):
        self.root.image_controller.update_image_list_eh.remove(self.update_valid_images)
        super().close()
