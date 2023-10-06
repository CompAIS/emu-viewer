import tkinter as tk
from tkinter import ttk

import ttkbootstrap as tb

from src.widgets.base_widget import BaseWidget


class ImageTableWidget(BaseWidget):
    label = "Image Table"
    dropdown = True

    def __init__(self, root):
        BaseWidget.__init__(self, root)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_num = 0  # Initialize the image number

        self.open_windows = []
        self.selected_image = self.root.image_controller.get_selected_image()
        self.open_images = self.root.image_controller.get_images()

        self.image_table()  # Create the image table widget

        self.root.image_controller.update_image_list_eh.add(self.update_images)

    def image_table(self):
        table = tb.Frame(self, bootstyle="light")
        table.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

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

    def update_images(self, selected_image, image_list):
        self.selected_image = selected_image
        self.open_images = image_list

        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, image in enumerate(self.open_images):
            self.add_image(i + 1, image.file_name)

        self.root.update()

    def close(self):
        self.root.image_controller.update_image_list_eh.remove(self.update_images)

        super().close()
