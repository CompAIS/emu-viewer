import tkinter as tk
from functools import partial

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


class HipsSelectorWidget(BaseWidget):
    label = "Hips Survey Selector"
    dropdown = False

    def __init__(self, root):
        super().__init__(root)
        # self.geometry("750x325")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.selected_projection = ""
        self.selected_hips_survey = ""
        self.selected_image_type = ""
        self.selected_wcs = None

        self.hips_survey = HipsSurvey()

        self.setup()

    def setup(self):
        frame = tb.Frame(self, bootstyle="light")
        frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        frame.columnconfigure((0, 1, 2, 3), weight=1)
        frame.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        col_widths = [23, 37]

        self.optical_dropdown = self.dropdown_options(
            frame,
            "Optical Hips Surveys",
            NO_SURVEY_SELECTED,
            optical_survey_options,
            self.select_optical_survey,
            col_widths[1],
            0,
            0,
        )

        self.infrared_dropdown = self.dropdown_options(
            frame,
            "Infrared Hips Surveys",
            NO_SURVEY_SELECTED,
            infrared_survey_options,
            self.select_infrared_survey,
            col_widths[1],
            0,
            1,
        )

        self.radio_dropdown = self.dropdown_options(
            frame,
            "Radio Hips Surveys",
            NO_SURVEY_SELECTED,
            radio_survey_options,
            self.select_radio_survey,
            col_widths[1],
            0,
            2,
        )

        self.xray_dropdown = self.dropdown_options(
            frame,
            "X-Ray Hips Surveys",
            NO_SURVEY_SELECTED,
            xray_survey_options,
            self.select_xray_survey,
            col_widths[1],
            0,
            3,
        )

        self.dropdown_options(
            frame,
            "Image Type",
            NO_IMAGE_TYPE_SELECTED,
            image_type_options,
            self.select_image_type,
            col_widths[1],
            0,
            5,
        )

        self.ra_entry = tb.Entry(frame, bootstyle="dark")
        self.dec_entry = tb.Entry(frame, bootstyle="dark")
        self.FOV_entry = tb.Entry(frame, bootstyle="dark")

        # Might remove when sorting out right click option
        valid_images = []
        for image in self.root.image_controller.get_images():
            if image.image_wcs is None:
                continue

            valid_images.append(image)

        self.dropdown_options(
            frame,
            "Open Images",
            NO_IMAGE_SELECTED,
            valid_images,
            self.select_image,
            col_widths[0],
            2,
            0,
        )

        self.ra_option(frame, "Ra", 2, 1)

        self.dec_option(frame, "Dec", 2, 2)

        self.FOV_option(frame, "FOV", 2, 3)

        self.dropdown_options(
            frame,
            "Projection",
            NO_PROJECTION_SELECTED,
            projection_options,
            self.select_projection,
            col_widths[0],
            2,
            4,
        )

        self.confirm_button(frame, "Select Survey", 3, 5)

    def select_image(self, image, dropdown):
        if image is None:
            self.selected_wcs = None
            dropdown["text"] = "No image selected"
            self.ra_entry.configure(state="enabled")
            self.dec_entry.configure(state="enabled")
            self.FOV_entry.configure(state="enabled")
        else:
            self.selected_wcs = image.image_wcs
            dropdown["text"] = image.file_name
            self.ra_entry.configure(state="disabled")
            self.dec_entry.configure(state="disabled")
            self.FOV_entry.configure(state="disabled")

    def ra_option(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.ra_entry.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

    def dec_option(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.dec_entry.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

    def FOV_option(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.FOV_entry.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
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

    def select_optical_survey(self, hips_survey, dropdown):
        self.selected_hips_survey = hips_survey
        dropdown["text"] = hips_survey
        self.infrared_dropdown["text"] = NO_SURVEY_SELECTED
        self.radio_dropdown["text"] = NO_SURVEY_SELECTED
        self.xray_dropdown["text"] = NO_SURVEY_SELECTED

    def select_infrared_survey(self, hips_survey, dropdown):
        self.selected_hips_survey = hips_survey
        dropdown["text"] = hips_survey
        self.optical_dropdown["text"] = NO_SURVEY_SELECTED
        self.radio_dropdown["text"] = NO_SURVEY_SELECTED
        self.xray_dropdown["text"] = NO_SURVEY_SELECTED

    def select_radio_survey(self, hips_survey, dropdown):
        self.selected_hips_survey = hips_survey
        dropdown["text"] = hips_survey
        self.optical_dropdown["text"] = NO_SURVEY_SELECTED
        self.infrared_dropdown["text"] = NO_SURVEY_SELECTED
        self.xray_dropdown["text"] = NO_SURVEY_SELECTED

    def select_xray_survey(self, hips_survey, dropdown):
        self.selected_hips_survey = hips_survey
        dropdown["text"] = hips_survey
        self.optical_dropdown["text"] = NO_SURVEY_SELECTED
        self.infrared_dropdown["text"] = NO_SURVEY_SELECTED
        self.radio_dropdown["text"] = NO_SURVEY_SELECTED

    def select_image_type(self, image_type, dropdown):
        self.selected_image_type = image_type
        dropdown["text"] = image_type

    def confirm_button(self, parent, text, gridX, gridY):
        button = tb.Button(
            parent,
            text=text,
            bootstyle="success",
            command=partial(self.select_survey),
        )
        button.grid(column=gridX, row=gridY, sticky=tk.SE, padx=10, pady=10)

    def select_survey(self):
        if self.selected_wcs is None:
            if (
                self.ra_entry.get() == ""
                or self.dec_entry.get() == ""
                or self.FOV_entry.get() == ""
                or self.selected_projection == ""
                or self.selected_hips_survey == ""
                or self.selected_image_type == ""
            ):
                return

            self.hips_survey.ra = float(self.ra_entry.get())
            self.hips_survey.dec = float(self.dec_entry.get())
            self.hips_survey.FOV = float(self.FOV_entry.get())
            self.hips_survey.projection = self.selected_projection
            self.hips_survey.survey = self.selected_hips_survey
            self.hips_survey.image_type = self.selected_image_type
        else:
            if (
                self.selected_projection == ""
                or self.selected_hips_survey == ""
                or self.selected_image_type == ""
            ):
                return

            self.hips_survey.projection = self.selected_projection
            self.hips_survey.survey = self.selected_hips_survey
            self.hips_survey.image_type = self.selected_image_type

        self.root.image_controller.open_hips(self.hips_survey, self.selected_wcs)
