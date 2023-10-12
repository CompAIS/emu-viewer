import tkinter as tk
from functools import partial
from tkinter import ttk

import ttkbootstrap as tb

from src.widgets.base_widget import BaseWidget


class StatisticsWidget(BaseWidget):
    label = "Statistics Table"
    dropdown = True

    def __init__(self, root):
        super().__init__(root)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_dropdown = None

        self.stats_window()

        self.root.image_controller.update_image_list_eh.add(self.update_open_images)

    def stats_window(self):
        self.window = tb.Frame(self, bootstyle="light")
        self.window.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        if self.root.image_controller.get_selected_image() is not None:
            if self.root.image_controller.get_selected_image().image_wcs is not None:
                self.image_options(
                    self.window,
                    "Select Image",
                    self.root.image_controller.get_selected_image().file_name,
                    0,
                    0,
                )

        self.image_stats_table(self.window, 0, 1)

    def image_options(self, parent, text, selected_option, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.image_dropdown = tb.Menubutton(
            parent, text=selected_option, bootstyle="dark"
        )
        self.image_dropdown.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

        self.update_dropdown(self.root.image_controller.get_images())

    def update_dropdown(self, image_list):
        dropdown_menu = tk.Menu(self.image_dropdown, tearoff=0)
        for image in image_list:
            if image.image_wcs is not None:
                dropdown_menu.add_command(
                    label=image.file_name,
                    command=partial(self.select_image, image.file_name),
                )

        self.image_dropdown["menu"] = dropdown_menu

    def select_image(self, option):
        self.image_dropdown["text"] = option

    def image_stats_table(self, parent, gridX, gridY):
        self.table = ttk.Treeview(parent, columns=("values"))
        self.table.grid(
            column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10, columnspan=2
        )
        self.table.heading("#0", text="Stat")
        self.table.heading("values", text="Value")
        # self.insert_row("Flux", "850")

    def insert_row(self, stat, value):
        self.table.insert("", tk.END, text=stat, values=value)

    def update_open_images(self, selected_image, image_list):
        if self.image_dropdown is None:
            if selected_image.image_wcs is not None:
                self.image_options(
                    self.window, "Select Image", selected_image.file_name, 0, 0
                )
        else:
            self.update_dropdown(image_list)

        self.root.update()

    def close(self):
        self.root.image_controller.update_image_list_eh.remove(self.update_open_images)
        super().close()
