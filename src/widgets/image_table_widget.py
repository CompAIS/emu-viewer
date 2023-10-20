import tkinter as tk

import ttkbootstrap as tb

from src.widgets.base_widget import BaseWidget
from src.widgets.components.table_widget import TableWidget


class ImageTableWidget(BaseWidget):
    label = "Image Table"
    dropdown = True

    def __init__(self, root):
        super().__init__(root)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.open_windows = []
        self.selected_image = self.root.image_controller.get_selected_image()
        self.open_images = self.root.image_controller.get_images()

        self.image_table()  # Create the image table widget

        self.root.image_controller.update_image_list_eh.add(self.update_images)

    def image_table(self):
        table_container = tb.Frame(self, bootstyle="light")
        table_container.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        label = tk.Label(table_container, text="Image Table")
        label.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.table = TableWidget(table_container, ["Num", "Image", "Matching"])
        self.table.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

        for i, image in enumerate(self.open_images):
            self.add_image(i + 1, image.file_name)

    def add_image(self, image_num, image_name):
        button_frame = tb.Frame(self.table, height=0)
        button_frame.grid_rowconfigure(0, weight=1, uniform="a")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="a")

        buttonXY = tb.Button(button_frame, text="XY")
        buttonXY.grid(row=0, column=0)
        buttonR = tb.Button(button_frame, text="R")
        buttonR.grid(row=0, column=1)
        buttonA = tb.Button(button_frame, text="A")
        buttonA.grid(row=0, column=2)

        self.table.add_row(
            tb.Label(self.table, text=f"{image_num}"),
            tb.Label(self.table, text=image_name),
            button_frame,
        )

    def update_images(self, selected_image, image_list):
        self.selected_image = selected_image
        self.open_images = image_list

        self.table.clear_rows()

        for i, image in enumerate(self.open_images):
            self.add_image(i + 1, image.file_name)

        self.root.update()

    def close(self):
        self.root.image_controller.update_image_list_eh.remove(self.update_images)

        super().close()
