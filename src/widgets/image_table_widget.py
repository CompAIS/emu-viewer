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

        self._cached_sel_image = None
        self._cached_image_list = None

        self.open_windows = []

        self.image_table()  # Create the image table widget

        self.root.image_controller.update_image_list_eh.add(self.on_image_list_change)
        self.root.image_controller.selected_image_eh.add(self.on_image_select)

    def image_table(self):
        table_container = tb.Frame(self, bootstyle="light")
        table_container.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
        table_container.grid_rowconfigure((0, 1), weight=0)
        table_container.grid_columnconfigure(0, weight=1)

        label = tk.Label(table_container, text="Image Table")
        label.grid(column=0, row=0, sticky="new", padx=10, pady=10)

        self.table = TableWidget(table_container, ["Num", "Image", "Matching"])
        self.table.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

        self.update_images()

    def update_images(self):
        """
        Update the image table with the current set of open images
        and the currently selected image.

        Will avoid updating when nothing has changed by storing a primitive cache.
        """

        open_images = self.root.image_controller.get_images()
        sel_image = self.root.image_controller.get_selected_image()
        if (
            self._cached_image_list == open_images
            and self._cached_sel_image == sel_image
        ):
            # nothing has changed
            print("ImageTable: not updating, nothing has changed!")

        self._cached_image_list = open_images
        self._cached_sel_image = sel_image

        self.table.clear_rows()

        for i, image in enumerate(open_images):
            self.add_image(i + 1, image)

        self.root.update()

    def add_image(self, image_num, image):
        button_frame = tb.Frame(self.table, height=0)
        button_frame.grid_rowconfigure(0, weight=1, uniform="a")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="a")

        for column, match_type in enumerate(MatchType):
            button = tb.Button(
                button_frame, text=match_type.value, bootstyle="primary-outline"
            )
            button.grid(row=0, column=column, padx=1, pady=1)
            button.configure(command=partial(self.on_match, button, match_type, image))

        font = ["Helvetica", 9]

        if image.is_selected():
            font.append("bold")

        font = tuple(font)

        self.table.add_row(
            tb.Label(self.table, text=f"{image_num}", font=font),
            tb.Label(self.table, text=image.file_name, font=font),
            button_frame,
        )

    # event handler for all match button presses
    def on_match(self, button, match_type, image):
        # update button style
        if image.is_matched(match_type):
            button.configure(bootstyle="primary-outline")
        else:
            button.configure(bootstyle="primary")

        # update image and everything downstream
        image.toggle_match(match_type)

    # wrapper funcs
    def on_image_list_change(self, selected_image, image_list):
        self.update_images()

    def on_image_select(self, selected_image):
        self.update_images()

    def close(self):
        self.root.image_controller.update_image_list_eh.remove(
            self.on_image_list_change
        )
        self.root.image_controller.selected_image_eh.remove(self.on_image_select)

        super().close()
