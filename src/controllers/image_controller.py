import tkinter as tk

import ttkbootstrap as tb

import src.lib.fits_handler as Fits_handler
import src.lib.hips_handler as Hips_handler
from src.widgets import image_widget as iw
from src.widgets.image_standalone_toplevel import StandaloneImage


# Create Image Controller Frame
class ImageController(tb.Frame):
    def __init__(self, parent, root):
        tb.Frame.__init__(self, parent, bootstyle="dark")

        self.root = root
        self.grid(column=1, row=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1, uniform="c")
        self.columnconfigure(0, weight=1, uniform="r")

        self.selected_image = -1

        # Add open_image as an event listener to open file
        root.menu_controller.open_file_eh.add(self.open_image)
        root.menu_controller.append_image_eh.add(self.append_image)
        root.menu_controller.open_hips_eh.add(self.open_hips)
        root.menu_controller.append_hips_eh.add(self.append_hips)

        self.main_image = None
        self.open_windows = []

        self.fits_image_data = {}

    def open_image(self, file_path):
        self.close_windows()

        image_data = Fits_handler.open_fits_file(file_path)
        self.fits_image_data[file_path] = image_data

        self.main_image = iw.ImageFrame(self, self.root, image_data)
        self.set_selected_image(0)

    def append_image(self, file_path):
        if self.main_image is None:
            self.open_image(file_path)
            return

        image_id = len(self.open_windows) + 1

        if self.fits_already_open(file_path):
            image_data = self.fits_image_data[file_path]
        else:
            image_data = Fits_handler.open_fits_file(file_path)
            self.fits_image_data[file_path] = image_data

        new_window = StandaloneImage(self, self.root, image_data, file_path, image_id)
        self.set_selected_image(image_id)

        self.open_windows.append(new_window)

    def open_hips(self, hips_survey):
        self.close_windows()

        image_data = Hips_handler.open_hips(hips_survey)

        self.main_image = iw.ImageFrame(self, self.root, image_data)
        self.set_selected_image(0)

    def append_hips(self, hips_survey):
        if self.main_image is None:
            self.open_hips(hips_survey)
            return

        image_id = len(self.open_windows) + 1

        image_data = Hips_handler.open_hips(hips_survey)

        new_window = StandaloneImage(self, self.root, image_data, hips_survey, image_id)
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
        for window in self.open_windows:
            window.destroy()

        self.open_windows = []
        self.set_selected_image(-1)

    def handle_focus(self, event):
        if self.selected_image != -1:
            self.set_selected_image(0)

        if self.root.widget_controller.open_windows["Render Configuration"] is None:
            return

        if self.selected_image == -1:
            return

        self.root.widget_controller.open_windows[
            "Render Configuration"
        ].update_selected_scaling(self.main_image.stretch)

        self.root.widget_controller.open_windows[
            "Render Configuration"
        ].update_selected_colour_map(self.main_image.colour_map)

        self.root.update()

    def fits_already_open(self, file_path):
        if self.fits_image_data.get(file_path) is not None:
            return True

        return False
