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


class HipsSelectorWidget(BaseWidget):
    label = "Hips Survey Selector"
    dropdown = False

    def __init__(self, root):
        super().__init__(root)

        self.selected_projection = ""
        self.selected_hips_survey = ""
        self.selected_image_type = ""
        self.selected_wcs = None

        self.hips_survey = HipsSurvey()

        self.setup()

        self.grab_set()

    def setup(self):
        frame = tb.Frame(self, width=100, bootstyle="light")
        frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        frame.columnconfigure((0, 1, 2, 3), weight=1)
        frame.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.ra_entry = tb.Entry(frame, bootstyle="dark")
        self.dec_entry = tb.Entry(frame, bootstyle="dark")
        self.FOV_entry = tb.Entry(frame, bootstyle="dark")

        self.image_options(frame, "Open Images", 0, 0)

        self.ra_option(frame, "Ra", 0, 1)

        self.dec_option(frame, "Dec", 0, 2)

        self.FOV_option(frame, "FOV", 0, 3)

        self.projection_options(frame, "Projection", self.selected_projection, 0, 4)

        self.optical_survey_options(
            frame, "Optical Hips Surveys", self.selected_hips_survey, 2, 1
        )

        self.infrared_survey_options(
            frame, "Infrared Hips Surveys", self.selected_hips_survey, 2, 2
        )

        self.radio_survey_options(
            frame, "Radio Hips Surveys", self.selected_hips_survey, 2, 3
        )

        self.xray_survey_options(
            frame, "X-Ray Hips Surveys", self.selected_hips_survey, 2, 4
        )

        self.image_type_options(frame, "Image Type", self.selected_image_type, 2, 0)

        self.confirm_button(frame, "Select Survey", 2, 5)

    def image_options(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown = tb.Menubutton(parent, text="No image selected", bootstyle="dark")
        dropdown.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown_menu = tk.Menu(dropdown, tearoff=0)

        dropdown_menu.add_command(
            label="No image selected",
            command=partial(self.select_image, None, dropdown),
        )

        valid_images = []
        for image in self.root.image_controller.get_images():
            if image.image_data_header is not None:
                valid_images.append(image)

        for option in valid_images:
            dropdown_menu.add_command(
                label=option.file_name,
                command=partial(self.select_image, option, dropdown),
            )

        dropdown["menu"] = dropdown_menu

    def select_image(self, image, menu_button):
        if image is None:
            self.selected_wcs = None
            menu_button["text"] = "No image selected"
            self.ra_entry.configure(state="enabled")
            self.dec_entry.configure(state="enabled")
            self.FOV_entry.configure(state="enabled")
        else:
            self.selected_wcs = image.image_wcs
            menu_button["text"] = image.file_name
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

    def projection_options(self, parent, text, selected_projection, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown = tb.Menubutton(parent, text=selected_projection, bootstyle="dark")
        dropdown.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown_menu = tk.Menu(dropdown, tearoff=0)

        for option in projection_options:
            dropdown_menu.add_command(
                label=option,
                command=partial(self.select_projection, option, dropdown),
            )

        dropdown["menu"] = dropdown_menu

    def select_projection(self, projection, menu_button):
        self.selected_projection = projection
        menu_button["text"] = projection

    def optical_survey_options(self, parent, text, selected_survey, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.optical_dropdown = tb.Menubutton(
            parent, text=selected_survey, bootstyle="dark"
        )
        self.optical_dropdown.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

        dropdown_menu = tk.Menu(self.optical_dropdown, tearoff=0)

        for option in optical_survey_options:
            dropdown_menu.add_command(
                label=option,
                command=partial(self.select_optical_survey, option),
            )

        self.optical_dropdown["menu"] = dropdown_menu

    def select_optical_survey(self, hips_survey):
        self.selected_hips_survey = hips_survey
        self.optical_dropdown["text"] = hips_survey
        self.infrared_dropdown["text"] = ""
        self.radio_dropdown["text"] = ""
        self.xray_dropdown["text"] = ""

    def infrared_survey_options(self, parent, text, selected_survey, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.infrared_dropdown = tb.Menubutton(
            parent, text=selected_survey, bootstyle="dark"
        )
        self.infrared_dropdown.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

        dropdown_menu = tk.Menu(self.optical_dropdown, tearoff=0)

        for option in infrared_survey_options:
            dropdown_menu.add_command(
                label=option,
                command=partial(self.select_infrared_survey, option),
            )

        self.infrared_dropdown["menu"] = dropdown_menu

    def select_infrared_survey(self, hips_survey):
        self.selected_hips_survey = hips_survey
        self.infrared_dropdown["text"] = hips_survey
        self.optical_dropdown["text"] = ""
        self.radio_dropdown["text"] = ""
        self.xray_dropdown["text"] = ""

    def radio_survey_options(self, parent, text, selected_survey, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.radio_dropdown = tb.Menubutton(
            parent, text=selected_survey, bootstyle="dark"
        )
        self.radio_dropdown.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

        dropdown_menu = tk.Menu(self.radio_dropdown, tearoff=0)

        for option in radio_survey_options:
            dropdown_menu.add_command(
                label=option,
                command=partial(self.select_radio_survey, option),
            )

        self.radio_dropdown["menu"] = dropdown_menu

    def select_radio_survey(self, hips_survey):
        self.selected_hips_survey = hips_survey
        self.radio_dropdown["text"] = hips_survey
        self.optical_dropdown["text"] = ""
        self.infrared_dropdown["text"] = ""
        self.xray_dropdown["text"] = ""

    def xray_survey_options(self, parent, text, selected_survey, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.xray_dropdown = tb.Menubutton(
            parent, text=selected_survey, bootstyle="dark"
        )
        self.xray_dropdown.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

        dropdown_menu = tk.Menu(self.xray_dropdown, tearoff=0)

        for option in xray_survey_options:
            dropdown_menu.add_command(
                label=option,
                command=partial(self.select_xray_survey, option),
            )

        self.xray_dropdown["menu"] = dropdown_menu

    def select_xray_survey(self, hips_survey):
        self.selected_hips_survey = hips_survey
        self.xray_dropdown["text"] = hips_survey
        self.optical_dropdown["text"] = ""
        self.infrared_dropdown["text"] = ""
        self.radio_dropdown["text"] = ""

    def image_type_options(self, parent, text, selected_survey, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.image_type_dropdown = tb.Menubutton(
            parent, text=selected_survey, bootstyle="dark"
        )
        self.image_type_dropdown.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

        dropdown_menu = tk.Menu(self.image_type_dropdown, tearoff=0)

        for option in image_type_options:
            dropdown_menu.add_command(
                label=option,
                command=partial(self.select_image_type, option),
            )

        self.image_type_dropdown["menu"] = dropdown_menu

    def select_image_type(self, type):
        self.selected_image_type = type
        self.image_type_dropdown["text"] = type

    def confirm_button(self, parent, text, gridX, gridY):
        button = tb.Button(
            parent,
            text=text,
            bootstyle="success",
            command=partial(self.select_survey),
        )
        button.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

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

        self.close()
