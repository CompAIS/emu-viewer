import tkinter as tk
import traceback
from functools import partial

import ttkbootstrap as tb
import ttkbootstrap.dialogs as dialogs

import src.widgets.image.image_controller as ic
from src.enums import DataType
from src.widgets.base_widget import BaseWidget
from src.widgets.hips_survey_selector.hips_handler import HipsSurvey

# All projection options available, can be edited to add more
projection_options = ["TAN", "ARC", "AIT", "SIN"]

# All optical survey options available, can be edited to add more
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

# All infrared survey options available, can be edited to add more
infrared_survey_options = [
    "CDS/P/unWISE/W1",
]

# All radio survey options available, can be edited to add more
radio_survey_options = [
    "CSIRO/P/RACS/low/I",
    "CSIRO/P/RACS/mid/I",
    "CDS/P/HI4PI/NHI",
]

# All x-ray survey options available, can be edited to add more
xray_survey_options = ["ov-gso/P/RASS"]

# All image type options available
data_type_options = [x.value for x in DataType]

# Empty dropdown strings to be displayed if no option selected or widget is reset
NO_IMAGE_SELECTED = "No Image Selected"
NO_PROJECTION_SELECTED = "No Projection Selected"
NO_SURVEY_SELECTED = "No Survey Selected"
NO_DATA_TYPE_SELECTED = "No Data Type Selected"

# All validation strings to be displayed if there is an error
INVALID_INPUT = "Invalid Input"
INVALID_SURVEY = "No survey selected, please select a survey"
INVALID_TYPE = "No type selected, please select a type"
INVALID_PROJECTION = "No projection selected, please select a projection"
INVALID_RA = "Invalid RA, please enter a float"
INVALID_DEC = "Invalid Dec, please enter a float"
INVALID_FOV = "Invalid FOV, please enter a float"
INVALID_FOV_LOW = "Invalid FOV, FOV must be greater then 0"
ERROR_GENERATING = "Error generating image, either incorrect survey has been entered or selected image is to large"

# Forced column widths for the dropdowns so that the dropdown box doesn't resize when selecting a dropdown option
COL_WIDTHS = [37, 23]


class HipsSelectorWidget(BaseWidget):
    """The HipsSelectorWidget is used to open a HiPs survey with specified parameters that can be selected manually or
    with a valid image"""

    label = "Hips Survey Selector"
    dropdown = False

    def __init__(self, root):
        """Initiates the hips selector widget

        Sets up the columns and rows of the window, all labels, dropdowns, entry boxes and buttons of the
        widget and adds the event to the image controllers event handler

        :param root: The main tkinter window of the application
        """
        super().__init__(root)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.selected_projection = None
        self.selected_hips_survey = None
        self.selected_data_type = None
        self.selected_wcs = None

        self.hips_survey = HipsSurvey()

        self.setup()

        ic.update_image_list_eh.add(self.update_valid_images)

    def setup(self):
        """
        Sets up all labels, dropdowns, entry boxes and buttons of the widget
        """

        # Base frame of the window setup with the rows and columns configured
        frame = tb.Frame(self, bootstyle="light")
        frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        frame.columnconfigure((0, 1, 2, 3), weight=1)
        frame.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Creates the optical label and dropdown with the specified optical survey options
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

        # Creates the infrared label and dropdown with the specified infrared survey options
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

        # Creates the radio label and dropdown with the specified radio survey options
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

        # Creates the x-ray label and dropdown with the specified x-ray survey options
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

        # Creates the custom survey label and entry box and binds it to the focus out event
        self.custom_survey = self.entry_options(frame, "Custom Survey", 0, 4)
        self.custom_survey.bind("<FocusOut>", self.custom_survey_focusout)

        # Creates the image type label and dropdown with the specified image type options
        self.data_type_dropdown = self.dropdown_options(
            frame,
            "Data Type",
            NO_DATA_TYPE_SELECTED,
            data_type_options,
            self.select_data_type,
            COL_WIDTHS[0],
            0,
            5,
        )

        # Create the image select label and dropdown with valid open images
        image_select_label = tb.Label(
            frame, text="Open Images", bootstyle="inverse-light"
        )
        image_select_label.grid(column=2, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.image_select_dropdown = tb.Menubutton(
            frame, text=NO_IMAGE_SELECTED, width=COL_WIDTHS[1], bootstyle="dark"
        )
        self.image_select_dropdown.grid(column=3, row=0, sticky=tk.EW, padx=10, pady=10)
        self.update_valid_images(None, ic.get_images())

        # Create the RA, DEC and FOV label and entry options
        self.ra_entry = self.entry_options(frame, "RA", 2, 1)
        self.dec_entry = self.entry_options(frame, "Dec", 2, 2)
        self.FOV_entry = self.entry_options(frame, "FOV", 2, 3)

        # Create the projection label and dropdown with the specified projection options
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

        # Create a frame to place the custom buttons inside of
        button_frame = tb.Frame(frame, bootstyle="light")
        button_frame.grid(column=2, columnspan=2, row=5, sticky=tk.NSEW)

        button_frame.columnconfigure((0, 1), weight=1)
        button_frame.rowconfigure(0, weight=1)

        # Create the reset button with the warning style
        self.custom_button(
            button_frame, "Reset", "warning", self.reset_all_options, 0, 0
        )
        # Create the select survey button with the success style
        self.custom_button(
            button_frame, "Select Survey", "success", self.select_survey, 1, 0
        )

    def dropdown_options(
        self, parent, text, dropdown_text, options, func, width, gridX, gridY
    ):
        """
        Generates a label and attached dropdown box at the specified grid positions of the parent
        :param parent: The frame to place the label and dropdown menu into
        :param text: Text to be used when creating the label
        :param dropdown_text: Text to be displayed before any dropdown option is selected
        :param options: The options to be added to the dropdown
        :param func: The function to be run when a dropdown option is selected
        :param width: The width to the set the dropdown to
        :param gridX: The x position of the label in the grid
        :param gridY: The y position of the label in the grid
        :return: The created dropdown for future referencing
        """
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
        """Set the projection to the selected option in the dropdown"""
        self.selected_projection = projection
        dropdown["text"] = projection

    def select_survey_option(self, hips_survey, dropdown):
        """Set the HiPs survey to the selected option in the dropdown"""
        self.clear_survey_options()
        self.selected_hips_survey = hips_survey
        dropdown["text"] = hips_survey

    def clear_survey_options(self):
        """Resets all survey options to default"""
        self.optical_dropdown["text"] = NO_SURVEY_SELECTED
        self.infrared_dropdown["text"] = NO_SURVEY_SELECTED
        self.radio_dropdown["text"] = NO_SURVEY_SELECTED
        self.xray_dropdown["text"] = NO_SURVEY_SELECTED
        self.custom_survey.delete(0, tk.END)

    def select_data_type(self, data_type: str, dropdown):
        """Set the data_type to the given data_type."""
        dropdown["text"] = data_type
        self.selected_data_type = DataType.from_str(data_type)

    def select_image(self, image, dropdown):
        """Determines whether to set the RA,DEC and FOV to a selected images values or not by disabling the
        corresponding entry boxes if an image is selected"""
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
        """
        Generates a label and an attached entry box at the specified grid positions of the parent
        :param parent: The frame to place the label and dropdown menu into
        :param text: Text to be used when creating the label
        :param gridX: The x position of the label in the grid
        :param gridY: The y position of the label in the grid
        :return: The created entry box for future referencing
        """
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        entry = tb.Entry(parent, bootstyle="dark")
        entry.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        return entry

    def custom_survey_focusout(self, event):
        """Event handler if the entry box for the custom survey entry box has lost focus"""
        self.custom_survey_enter()

    def custom_survey_enter(self):
        """
        Changes the selected option to the custom survey entry box and resets all the appropriate dropdown options
        :return: If the entry box is empty return
        """
        if self.custom_survey.get() == "":
            return

        self.selected_hips_survey = self.custom_survey.get()
        self.optical_dropdown["text"] = NO_SURVEY_SELECTED
        self.infrared_dropdown["text"] = NO_SURVEY_SELECTED
        self.radio_dropdown["text"] = NO_SURVEY_SELECTED
        self.xray_dropdown["text"] = NO_SURVEY_SELECTED

    def custom_button(self, parent, text, style, func, gridX, gridY):
        """
        Generates a custom button at the specified grid positions of the parent and with a specified style and function
        to run on click
        :param parent: The frame to place the button into
        :param text: Text to be used when creating the button
        :param style: The style to use when creating a button
        :param func: The function to be executed when clicking the button
        :param gridX: The x position of the button in the grid
        :param gridY: The y position of the button in the grid
        """
        button = tb.Button(
            parent,
            text=text,
            bootstyle=style,
            command=partial(func),
        )
        button.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

    def reset_all_options(self):
        """Resets all options in the widget back to default"""
        self.selected_projection = None
        self.selected_hips_survey = None
        self.selected_data_type = None
        self.selected_wcs = None

        self.clear_survey_options()
        self.data_type_dropdown["text"] = NO_DATA_TYPE_SELECTED

        self.image_select_dropdown["text"] = NO_IMAGE_SELECTED
        self.ra_entry.delete(0, tk.END)
        self.dec_entry.delete(0, tk.END)
        self.FOV_entry.delete(0, tk.END)
        self.projection_dropdown["text"] = NO_PROJECTION_SELECTED

    def select_survey(self):
        """Opens a survey based on all the selected options and validates that they are either not empty or in the
        correct format required and returns if any validation fails"""
        self.custom_survey_enter()

        if self.selected_hips_survey is None:
            self.validation_error(INVALID_INPUT, INVALID_SURVEY)
            return
        self.hips_survey.survey = self.selected_hips_survey

        if self.selected_data_type is None:
            self.validation_error(INVALID_INPUT, INVALID_TYPE)
            return
        self.hips_survey.data_type = self.selected_data_type

        if self.selected_projection is None:
            self.validation_error(INVALID_INPUT, INVALID_PROJECTION)
            return
        self.hips_survey.projection = self.selected_projection

        if self.selected_wcs is None:
            self.hips_survey.ra = self.float_validation(
                self.ra_entry, INVALID_INPUT, INVALID_RA
            )
            if self.hips_survey.ra == "F":
                return

            self.hips_survey.dec = self.float_validation(
                self.dec_entry, INVALID_INPUT, INVALID_DEC
            )
            if self.hips_survey.dec == "F":
                return

            self.hips_survey.FOV = self.float_validation(
                self.FOV_entry, INVALID_INPUT, INVALID_FOV
            )
            if self.hips_survey.FOV == "F":
                return

            if float(self.hips_survey.FOV) <= 0:
                self.validation_error(INVALID_INPUT, INVALID_FOV_LOW)
                return

        try:
            ic.open_hips(self, self.hips_survey, self.selected_wcs)
        except AttributeError as e:
            traceback.print_exc()
            self.validation_error("Error", ERROR_GENERATING)
            return

    def validation_error(self, title, error):
        """
        Displays an error messagebox if any validation fails
        :param title: The text to be displayed in the title bar of the messagebox
        :param error: The text to be displayed inside the messagebox
        """
        dialogs.Messagebox.show_error(
            error,
            parent=self,
            title=title,
            alert=False,
        )

    def float_validation(self, entry, title, error):
        """
        Validates whether the text in the entry box is a float
        :param entry: The entry box to be checked
        :param title: The text to be displayed in the title bar of a messagebox if an error occurs
        :param error: The text to be displayed inside the messagebox if an error occurs
        :return: Either a valid float value or a string to be used to cancel opening a survey
        """
        try:
            valid_float = float(entry.get())
        except ValueError:
            self.validation_error(title, error)
            return "F"

        return valid_float

    def update_valid_images(self, selected_image, image_list):
        """Updates the valid images to be used if selecting to open a HiPs survey based on an open image

        :param selected_image: The currently selected open image
        :param image_list: The list of all currently open images
        """
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
        """Sets the RA and DEC entry boxes to specified values

        :param ra: Value to set the RA entry box
        :param dec: Value to set the DEC entry box
        """
        self.ra_entry.delete(0, tk.END)
        self.ra_entry.insert(0, ra)
        self.dec_entry.delete(0, tk.END)
        self.dec_entry.insert(0, dec)

    def close(self):
        """Closes the widget and removes any active event handlers"""
        ic.update_image_list_eh.remove(self.update_valid_images)
        super().close()
