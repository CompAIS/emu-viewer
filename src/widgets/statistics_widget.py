import tkinter as tk
from functools import partial

import ttkbootstrap as tb


class StatisticsWidget(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.title("Statistics Table")
        self.root = root

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_dropdown = None
        self.selected_image = self.root.image_controller.get_selected_image()

        self.open_images = [self.root.image_controller.main_image]
        for images in self.root.image_controller.open_windows:
            self.open_images.append(images.image_frame)

        self.stats_window()

        self.protocol(
            "WM_DELETE_WINDOW", self.root.widget_controller.close_statistics_widget
        )

    def stats_window(self):
        self.window = tb.Frame(self, bootstyle="light")
        self.window.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        if self.selected_image is not None:
            self.image_options(
                self.window, "Select Image", self.selected_image.file_name, 0, 0
            )

    def image_options(self, parent, text, selected_option, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.image_dropdown = tb.Menubutton(
            parent, text=selected_option, bootstyle="dark"
        )
        self.image_dropdown.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

        dropdown_menu = tk.Menu(self.image_dropdown, tearoff=0)

        for option in self.open_images:
            dropdown_menu.add_command(
                label=option.file_name,
                command=partial(self.select_image, option.file_name),
            )

        self.image_dropdown["menu"] = dropdown_menu

    def select_image(self, option):
        self.selected_image = option
        self.image_dropdown["text"] = option

    def update_open_images(self):
        self.selected_image = self.root.image_controller.get_selected_image()

        self.open_images = [self.root.image_controller.main_image]
        for images in self.root.image_controller.open_windows:
            self.open_images.append(images.image_frame)

        if self.image_dropdown is None:
            self.image_options(
                self.window, "Select Image", self.selected_image.file_name, 0, 0
            )
        else:
            self.update_image_options()

        self.root.update()

    def update_image_options(self):
        dropdown_menu = tk.Menu(self.image_dropdown, tearoff=0)

        for option in self.open_images:
            dropdown_menu.add_command(
                label=option.file_name,
                command=partial(self.select_image, option.file_name),
            )

        self.image_dropdown["menu"] = dropdown_menu
