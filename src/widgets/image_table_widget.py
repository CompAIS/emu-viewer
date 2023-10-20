import tkinter as tk
from functools import partial

import ttkbootstrap as tb

from src.lib.match_type import MatchType
from src.widgets.base_widget import BaseWidget
from src.widgets.components.table_widget import TableWidget


class ImageTableWidget(BaseWidget):
    label = "Image Table"
    dropdown = True

    def __init__(self, root):
        super().__init__(root)
        self.geometry("500x300")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # self.grid_propagate(False)

        self.open_windows = []
        self.selected_image = self.root.image_controller.get_selected_image()
        self.open_images = self.root.image_controller.get_images()

        self.image_table()  # Create the image table widget

        self.root.image_controller.update_image_list_eh.add(self.update_images)

    def image_table(self):
        table_container = tb.Frame(self, bootstyle="light")
        table_container.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
        table_container.grid_rowconfigure((0, 1), weight=0)
        table_container.grid_columnconfigure(0, weight=1)

        label = tk.Label(table_container, text="Image Table")
        label.grid(column=0, row=0, sticky="new", padx=10, pady=10)

        self.table = TableWidget(table_container, ["Num", "Image", "Matching"])
        self.table.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

        for i, image in enumerate(self.open_images):
            self.add_image(i + 1, image)

    def add_image(self, image_num, image):
        button_frame = tb.Frame(self.table, height=0)
        button_frame.grid_rowconfigure(0, weight=1, uniform="a")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="a")

        buttonXY = tb.Button(button_frame, text="XY", bootstyle="primary-outline")
        buttonXY.grid(row=0, column=0, padx=1, pady=1)
        buttonXY.configure(
            command=partial(self.on_match, buttonXY, MatchType.COORD, image)
        )

        buttonR = tb.Button(button_frame, text="R", bootstyle="primary-outline")
        buttonR.grid(row=0, column=1, padx=1, pady=1)
        buttonR.configure(
            command=partial(self.on_match, buttonR, MatchType.RENDER, image)
        )

        buttonA = tb.Button(button_frame, text="A", bootstyle="primary-outline")
        buttonA.grid(row=0, column=2, padx=1, pady=1)
        buttonA.configure(
            command=partial(self.on_match, buttonA, MatchType.ANNOTATION, image)
        )

        self.table.add_row(
            tb.Label(self.table, text=f"{image_num}", justify="center"),
            tb.Label(self.table, text=image.file_name, justify="center"),
            button_frame,
        )

    def update_images(self, selected_image, image_list):
        self.selected_image = selected_image
        self.open_images = image_list

        self.table.clear_rows()

        for i, image in enumerate(self.open_images):
            self.add_image(i + 1, image)

        self.root.update()

    def on_match(self, button, match_type, image, *args, **kwargs):
        if image.is_matched(match_type):
            button.configure(bootstyle="primary-outline")
        else:
            button.configure(bootstyle="primary")

        image.toggle_match(match_type)

    def close(self):
        self.root.image_controller.update_image_list_eh.remove(self.update_images)

        super().close()
