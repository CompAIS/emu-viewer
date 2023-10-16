import tkinter as tk
from tkinter import ttk

import ttkbootstrap as tb

from src.widgets.base_widget import BaseWidget


class ImageTableWidget(BaseWidget):
    label = "Image Table"
    dropdown = True

    def __init__(self, root):
        super().__init__(root)

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self.open_windows = []
        self.selected_image = self.root.image_controller.get_selected_image()
        self.open_images = self.root.image_controller.get_images()

        coord_match = tb.Button(self, text="Coord match", command=self.coord_matching)
        coord_match.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        render_match = tb.Button(
            self, text="Render match", command=self.render_matching
        )
        render_match.grid(column=1, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.image_table()  # Create the image table widget

        self.root.image_controller.update_image_list_eh.add(self.update_images)
        self.root.image_controller.selected_image_eh.add(self.update_selected_image)

    def image_table(self):
        table = tb.Frame(self, bootstyle="light")
        table.grid(column=0, columnspan=2, row=1, sticky=tk.NSEW, padx=10, pady=10)

        label = tk.Label(table, text="Image Table")
        label.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table, columns=("Num", "Image", "Coords Matching", "Render Matching")
        )
        self.tree.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        self.tree.heading("#0", text="Num")
        self.tree.heading("#1", text="Image")
        self.tree.heading("#2", text="Coords Matching")
        self.tree.heading("#3", text="Render Matching")
        self.tree.grid(column=0, row=1, sticky="nsew")
        for i, image in enumerate(self.open_images):
            self.add_image(i + 1, image.file_name)

    def add_image(self, image_num, image_name):
        self.tree.insert("", "end", values=(image_num, image_name, "", ""))

    def coord_matching(self):
        limits = self.selected_image.limits

        for image in self.open_images:
            image.set_limits(limits)
            image.update_limits()
            image.add_coords_event()
            self.root.image_controller.coords_matched.append(image)

        self.root.update()

    def render_matching(self):
        colour_map = self.selected_image.colour_map
        stretch = self.selected_image.stretch
        percentile = self.selected_image.selected_percentile

        for image in self.open_images:
            image.set_colour_map(colour_map)
            image.update_colour_map()
            image.set_scaling(stretch)
            image.set_selected_percentile(percentile)
            image.update_norm()
            self.root.image_controller.render_matched.append(image)

        self.root.update()

    def update_images(self, selected_image, image_list):
        self.selected_image = selected_image
        self.open_images = image_list

        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, image in enumerate(self.open_images):
            self.add_image(i + 1, image.file_name)

        self.root.update()

    def update_selected_image(self, selected_image):
        self.selected_image = selected_image

    def close(self):
        self.root.image_controller.update_image_list_eh.remove(self.update_images)
        self.root.image_controller.selected_image_eh.remove(self.update_selected_image)
        super().close()
