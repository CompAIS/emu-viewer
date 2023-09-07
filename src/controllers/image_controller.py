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
        root.menu_controller.append_image_eh.add(self.append_image)
        self.main_image = None
        self.open_windows = []

    def open_image(self, file_path):
        self.main_image = iw.ImageFrame(self, self.root, file_path)
        self.close_windows()

    def append_image(self, file_path):
        if self.main_image is None:
            self.open_image(self, file_path)
            return

        file_name = os.path.basename(file_path)

        new_window = tk.Toplevel(self.root)
        new_window.title(file_name)
        new_window.geometry("800x600")
        new_window.rowconfigure(0, weight=1)
        new_window.columnconfigure(0, weight=1)

        new_image = iw.ImageFrame(new_window, self.root, file_path)
        self.open_windows.append(new_window)

    def close_windows(self):
        for window in self.open_windows:
            window.destroy()
        self.open_windows = []
