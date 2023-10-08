import os
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as tb

import src.lib.fits_handler as Fits_handler
import src.lib.hips_handler as Hips_handler
from src.lib.event_handler import EventHandler
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

        self.selected_image = None

        # Add open_image as an event listener to open file
        root.menu_controller.open_file_eh.add(self.open_image)
        root.menu_controller.append_image_eh.add(self.append_image)
        root.menu_controller.open_hips_eh.add(self.open_hips)
        root.menu_controller.append_hips_eh.add(self.append_hips)

        self.main_image = None
        self.open_windows = []

        self.fits_image_data = {}

        self.selected_image_eh = EventHandler()
        self.update_image_list_eh = EventHandler()

    def open_image(self, file_path):
        t = "You are opening another Image. Changes made will reset. Do you want to continue?"
        if self.get_selected_image() is not None and not messagebox.askyesno(
            title="Confirmation", message=t
        ):
            return

        self.close_windows()

        image_data, image_data_header = Fits_handler.open_fits_file(file_path)
        self.fits_image_data[file_path] = image_data

        file_name = os.path.basename(file_path)

        self.main_image = iw.ImageFrame(
            self, self.root, image_data, image_data_header, file_name
        )
        self.set_selected_image(self.main_image)

        self.update_image_list_eh.invoke(self.get_selected_image(), self.get_images())

    def append_image(self, file_path):
        if self.main_image is None:
            self.open_image(file_path)
            return

        if self.fits_already_open(file_path):
            # TODO save image header in fit_image_data with tuple???
            # image_data = self.fits_image_data[file_path]
            image_data, image_data_header = Fits_handler.open_fits_file(file_path)
        else:
            image_data, image_data_header = Fits_handler.open_fits_file(file_path)
            self.fits_image_data[file_path] = image_data

        file_name = os.path.basename(file_path)

        new_window = StandaloneImage(
            self, self.root, image_data, image_data_header, file_name
        )
        self.open_windows.append(new_window)
        self.set_selected_image(new_window)

        self.update_image_list_eh.invoke(self.get_selected_image(), self.get_images())

    def open_hips(self, hips_survey):
        self.close_windows()

        image_data, image_header = Hips_handler.open_hips(hips_survey)

        self.main_image = iw.ImageFrame(
            self, self.root, image_data, image_header, hips_survey.survey
        )
        self.set_selected_image(self.main_image)

        self.update_image_list_eh.invoke(self.get_selected_image(), self.get_images())

    def append_hips(self, hips_survey):
        if self.main_image is None:
            self.open_hips(hips_survey)
            return

        image_data, image_header = Hips_handler.open_hips(hips_survey)

        new_window = StandaloneImage(
            self, self.root, image_data, hips_survey.survey, hips_survey.survey
        )

        self.open_windows.append(new_window)
        self.set_selected_image(new_window)

        self.update_image_list_eh.invoke(self.get_selected_image(), self.get_images())

    def get_selected_image(self):
        if self.selected_image is None:
            return None  # No image loaded so nothing to select

        if isinstance(self.selected_image, StandaloneImage):
            return self.selected_image.image_frame

        return self.selected_image

    def get_images(self):
        if self.main_image is None:
            return []

        images = [self.main_image]
        for w in self.open_windows:
            images.append(w.image_frame)

        return images

    def set_selected_image(self, image):
        self.selected_image = image

        self.selected_image_eh.invoke(self.get_selected_image())

    def close_windows(self):
        for window in self.open_windows:
            window.destroy()

        self.open_windows = []
        self.set_selected_image(None)

    def handle_focus(self, event):
        if self.selected_image is None:
            return

        self.set_selected_image(self.main_image)

    def fits_already_open(self, file_path):
        if self.fits_image_data.get(file_path) is not None:
            return True

        return False

    def close_appended_image(self, image):
        image.destroy()
        self.open_windows.remove(image)

        self.set_selected_image(self.main_image)
        self.update_image_list_eh.invoke(self.get_selected_image(), self.get_images())
