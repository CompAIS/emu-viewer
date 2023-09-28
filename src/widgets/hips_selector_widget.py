import tkinter as tk
from functools import partial

import ttkbootstrap as tb

hips_survey_options = ["CDS/P/DSS2/red", "CDS/P/DSS2/blue"]


class HipsSelectorWidget(tk.Toplevel):
    def __init__(self, parent, root):
        tk.Toplevel.__init__(self, root)
        self.parent = parent
        self.root = root

        self.title("Hips Survey Selector")

        self.selected_hips_survey = ""

        frame = tb.Frame(self, width=100, bootstyle="light")
        frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.hips_survey_select(frame, "Select Hips Survey", 0, 0)

        button = tb.Button(
            frame,
            text="Select Survey",
            bootstyle="dark",
            command=partial(self.select_survey),
        )
        button.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.close_without_select)

    def hips_survey_select(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown = tb.Menubutton(
            parent, text=self.selected_hips_survey, bootstyle="dark"
        )
        dropdown.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown_menu = tk.Menu(dropdown, tearoff=0)

        for option in hips_survey_options:
            dropdown_menu.add_command(
                label=option,
                command=partial(self.select_hips_survey, option, dropdown),
            )

        dropdown["menu"] = dropdown_menu

    def select_hips_survey(self, hips_survey, menu_button):
        self.selected_hips_survey = hips_survey
        menu_button["text"] = hips_survey

    def select_survey(self):
        if self.selected_hips_survey == "":
            return

        self.destroy()

    def close_without_select(self):
        self.selected_hips_survey = ""
        self.destroy()
