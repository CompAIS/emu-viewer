import tkinter as tk

import ttkbootstrap as tb

from src.widgets import image_widget as iw
from src.widgets.image_standalone_toplevel import StandaloneImage


# Create Image Controller Frame
class ImageController(tb.Frame):
    def __init__(self, parent, root):
        tb.Frame.__init__(self, parent, bootstyle="dark")

        self.root = root
        self.toolbar
        self.grid(column=1, row=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1, uniform="c")
        self.columnconfigure(0, weight=1, uniform="r")

        self.selected_image = -1

        # Add open_image as an event listener to open file
        root.menu_controller.open_file_eh.add(self.open_image)
        root.menu_controller.append_image_eh.add(self.append_image)
        self.main_image = None
        self.open_windows = []

    def open_image(self, file_path):
        self.close_windows()
        self.main_image = iw.ImageFrame(self, self.root, file_path)
        self.set_selected_image(0)

    def append_image(self, file_path):
        if self.main_image is None:
            self.open_image(file_path)
            return

        image_id = len(self.open_windows) + 1
        new_window = StandaloneImage(self, file_path, image_id, self.toolbar)
        self.set_selected_image(image_id)

        self.open_windows.append(new_window)

    def get_selected_image(self):
        if self.selected_image == -1:
            return None  # No image loaded so nothing to select

        if self.selected_image == 0:
            return self.main_image

        return self.open_windows[self.selected_image - 1].image_frame

    def get_images(self):
        images = [self.main_image]
        for w in self.open_windows:
            images.append(w.image_frame)

        return images

    def set_selected_image(self, image):
        self.selected_image = image

    def close_windows(self):
        if self.main_image is not None:
            self.main_image.close()

        for window in self.open_windows:
            window.image_frame.close()
            window.destroy()

        self.open_windows = []
        self.set_selected_image(-1)

    def handle_focus(self, event):
        self.set_selected_image(0)
