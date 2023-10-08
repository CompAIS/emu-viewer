import tkinter as tk
from functools import partial

import ttkbootstrap as tb

from src.widgets.base_widget import BaseWidget

NOTHING_OPEN = "No image open"


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
        self.update_dropdown(
            self.root.image_controller.get_selected_image(),
            self.root.image_controller.get_images(),
        )

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

        mean_entry = tb.Entry(self.frame)
        mean_entry.grid(column=1, row=2, padx=10, pady=10)

        sigma_label = tb.Label(self.frame, text="Sigma", bootstyle="inverse-light")
        sigma_label.grid(column=0, row=3, padx=10, pady=10, sticky=tk.W)

        sigma_entry = tb.Entry(self.frame)
        sigma_entry.grid(column=1, row=3, padx=10, pady=10)

        sigmas_label = tb.Label(
            self.frame, text="Sigma List", bootstyle="inverse-light"
        )
        sigmas_label.grid(column=0, row=4, padx=10, pady=10, sticky=tk.W)

        sigmas_entry = tb.Entry(self.frame)
        sigmas_entry.grid(column=1, row=4, padx=10, pady=10)

        # Generate Levels
        generate_button = tb.Button(self.frame, text="Generate", bootstyle="success")
        generate_button.grid(column=0, row=5, columnspan=2, padx=10, pady=(10, 20))

        # Levels
        levels_label = tb.Label(self.frame, text="Levels", bootstyle="inverse-light")
        levels_label.grid(column=0, row=6, padx=10, pady=10, sticky=tk.W)

        levels_entry = tb.Entry(self.frame)
        levels_entry.grid(column=1, columnspan=2, row=6, padx=10, pady=10)

        # Apply / Close buttons
        self.buttons = tb.Frame(self.frame, bootstyle="light")
        self.buttons.grid(column=1, row=7, sticky=tk.NSEW, padx=10, pady=10)
        self.buttons.rowconfigure(0, weight=1)
        self.buttons.columnconfigure(0, weight=1)

        self.clear_button = tb.Button(self.buttons, bootstyle="warning", text="Clear")
        self.clear_button.grid(column=0, row=0, sticky=tk.SE)

        self.apply_button = tb.Button(
            self.buttons, bootstyle="success", text="Apply", command=self.apply_contours
        )
        self.apply_button.grid(column=1, row=0, sticky=tk.SE)

        self.close_button = tb.Button(
            self.buttons, bootstyle="danger-outline", text="Close", command=self.close
        )
        self.close_button.grid(column=2, row=0, sticky=tk.SE, padx=(10, 0))

    def get_data_source(self):
        return self.data_source

    def set_data_source(self, image):
        if image is None:
            self.data_source = None
            self.data_source_dropdown["text"] = NOTHING_OPEN
            return

        self.data_source = image
        self.data_source_dropdown["text"] = image.file_name

    def update_dropdown(self, selected_image, image_list):
        # Always change the commands to match the current list
        self.data_source_menu = tk.Menu(self.data_source_dropdown)  # TODO set tearoff
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

    def apply_contours(self):
        """
        We clicked "Apply".
        """

        self.root.image_controller.get_selected_image().contour_levels = [
            158.91,
            314.95,
            627.02,
        ]
        # self.root.image_controller.get_selected_image().update_image_render()
