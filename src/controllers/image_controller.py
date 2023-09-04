import ttkbootstrap as tb

from src.widgets import image_widget as iw
import tkinter as tk


# Create Image Controller Frame
class ImageController(tb.Frame):
    def __init__(self, parent, root):
        tb.Frame.__init__(
            self,
            parent,
            bootstyle="dark",
        )

        self.grid(
            column=1,
            row=0,
            sticky=tk.NSEW,
        )

        self.root = root
        self.rowconfigure(0, weight=1, uniform="c")
        self.columnconfigure(0, weight=1, uniform="r")

        # Add open_image as an event listener to open file
        root.menu_controller.open_file_eh.add(self.open_image)
        self.open_images = []

    # Open image file based on path selected
    def open_image(self, file_path):
        gridX = len(self.open_images) % 2
        gridY = len(self.open_images) // 2
        new_image = iw.ImageFrame(self, self.root, file_path, gridX, gridY)

        # if we are about to expand into the second column, configure it
        if len(self.open_images) == 1:
            self.columnconfigure(1, weight=1, uniform="c")

        # if we are about to expand into a new row, configure it
        if gridY == 1:
            self.rowconfigure(gridX, weight=1, uniform="r")

        self.open_images.append(new_image)
