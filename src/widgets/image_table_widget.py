import tkinter as tk

import ttkbootstrap as tb

from src.widgets.base_widget import BaseWidget


class ImageTableWidget(BaseWidget):
    label = "Image Table"
    dropdown = True

    def __init__(self, root):
        BaseWidget.__init__(self, root)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_table()

    def image_table(self):
        table = tb.Frame(self, bootstyle="light")
        table.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
        table.grid_propagate(0)

        label = tb.Label(table, text="Image Table", bootstyle="success")
        label.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
