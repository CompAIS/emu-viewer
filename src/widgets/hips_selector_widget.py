import tkinter as tk
from functools import partial

import ttkbootstrap as tb

from src.lib.hips_handler import HipsSurvey

projection_options = ["TAN", "ARC", "AIT"]
hips_survey_options = [
    "CDS/P/skymapper-R",
    "CDS/P/DSS2/red",
]


class HipsSelectorWidget(tk.Toplevel):
    def __init__(self, parent, root):
        tk.Toplevel.__init__(self, root)
        self.parent = parent
        self.root = root

        self.title("Hips Survey Selector")
        self.resizable(0, 0)

        self.selected_projection = ""
        self.selected_hips_survey = ""

        self.hips_survey = HipsSurvey()

        self.setup()

        self.protocol("WM_DELETE_WINDOW", self.close_without_select)

        self.grab_set()

    def setup(self):
        frame = tb.Frame(self, width=100, bootstyle="light")
        frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.ra_option(frame, "Ra", 0, 0)

        self.dec_option(frame, "Dec", 0, 1)

        self.FOV_option(frame, "FOV", 0, 2)

        self.projection_options(frame, "Projection", self.selected_projection, 0, 3)

        self.survey_options(frame, "Hips Survey", self.selected_hips_survey, 0, 4)

        self.confirm_button(frame, "Select Survey", 0, 5)

    def ra_option(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.ra_entry = tb.Entry(parent, bootstyle="dark")
        self.ra_entry.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

    def dec_option(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.dec_entry = tb.Entry(parent, bootstyle="dark")
        self.dec_entry.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

    def FOV_option(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.FOV_entry = tb.Entry(parent, bootstyle="dark")
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

    def survey_options(self, parent, text, selected_survey, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown = tb.Menubutton(parent, text=selected_survey, bootstyle="dark")
        dropdown.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown_menu = tk.Menu(dropdown, tearoff=0)

        for option in hips_survey_options:
            dropdown_menu.add_command(
                label=option,
                command=partial(self.select_hips_survey, option, dropdown),
            )

        dropdown["menu"] = dropdown_menu

    def confirm_button(self, parent, text, gridX, gridY):
        button = tb.Button(
            parent,
            text=text,
            bootstyle="dark",
            command=partial(self.select_survey),
        )
        button.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

    def select_hips_survey(self, hips_survey, menu_button):
        self.selected_hips_survey = hips_survey
        menu_button["text"] = hips_survey

    def select_survey(self):
        if (
            self.ra_entry.get() == ""
            or self.dec_entry.get() == ""
            or self.FOV_entry.get() == ""
            or self.selected_projection == ""
            or self.selected_hips_survey == ""
        ):
            return

        self.hips_survey.ra = float(self.ra_entry.get())
        self.hips_survey.dec = float(self.dec_entry.get())
        self.hips_survey.FOV = self.FOV_entry.get()
        self.hips_survey.projection = self.selected_projection
        self.hips_survey.survey = self.selected_hips_survey

        self.destroy()

    def close_without_select(self):
        self.destroy()
