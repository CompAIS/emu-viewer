import os  # Used to obtain file name from path
import tkinter as tk

import ttkbootstrap as tb

from src.widgets import image_widget as iw


# Create Image Controller Frame
class ImageController(tb.Frame):
    def __init__(self, parent, root):
        tb.Frame.__init__(self, parent, bootstyle="dark")

        self.root = root
        self.grid(column=1, row=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1, uniform="c")
        self.columnconfigure(0, weight=1, uniform="r")

        # Add open_image as an event listener to open file
        root.menu_controller.open_file_eh.add(self.open_image)
        root.menu_controller.open_window_eh.add(self.open_window)
        self.open_images = []

    def open_image(self, file_path):
        new_image = iw.ImageFrame(self, self.root, file_path)
        self.open_images.append(new_image)

    def open_window(self, file_path):
        # Extract the file name from the file path
        file_name = os.path.basename(file_path)

        # Create a secondary (or popup) window with the image file name as the title
        secondary_window = tk.Toplevel(self.root)
        secondary_window.title(file_name)
        secondary_window.geometry("800x600")

        # Remove padding and border around the ImageFrame
        new_image = iw.ImageFrame(secondary_window, self.root, file_path)
        new_image.pack(fill="both", expand=True)  # Fill the available space
        self.open_images.append(new_image)
