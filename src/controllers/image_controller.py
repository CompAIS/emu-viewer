import os
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as tb

import src.lib.fits_handler as Fits_handler
import src.lib.hips_handler as Hips_handler
import src.lib.png_handler as png_handler
from src.lib.event_handler import EventHandler
from src.widgets import image_widget as iw
from src.widgets.image_standalone_toplevel import StandaloneImage

CLOSE_CONFIRM = "Are you sure you want to close all currently open images? All changes will not be saved."


# Create Image Controller Frame
class ImageController(tb.Frame):
    def __init__(self, parent, root):
        super().__init__(parent, bootstyle="dark")

        self.root = root
        self.grid(column=1, row=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1, uniform="c")
        self.columnconfigure(0, weight=1, uniform="r")

        self.selected_image = None

        # Add open_image as an event listener to open file
        root.menu_controller.open_fits_eh.add(self.open_fits)
        root.menu_controller.open_png_eh.add(self.open_png)
        root.menu_controller.open_hips_eh.add(self.open_hips)
        root.menu_controller.close_images_eh.add(self.close_images)

        self.main_image = None
        self.open_windows = []

        self.selected_image_eh = EventHandler()
        self.update_image_list_eh = EventHandler()

    def open_image(self, image_data, image_data_header, file_name, file_type):
        if self.main_image is None:
            self.main_image = iw.ImageFrame(
                self, self.root, image_data, image_data_header, file_name, file_type
            )
            self.set_selected_image(self.main_image)
        else:
            new_window = StandaloneImage(
                self, self.root, image_data, image_data_header, file_name, file_type
            )
            self.open_windows.append(new_window)
            self.set_selected_image(new_window)

        self.update_image_list_eh.invoke(self.get_selected_image(), self.get_images())

    def open_fits(self, file_path):
        image_data, image_data_header = Fits_handler.open_fits_file(file_path)
        file_name = os.path.basename(file_path)
        self.open_image(image_data, image_data_header, file_name, "fits")

    def open_png(self, file_path):
        image_data = png_handler.open_png_file(file_path)
        file_name = os.path.basename(file_path)
        self.open_image(image_data, None, file_name, "png")

    def open_hips(self, hips_survey, wcs):
        try:
            if wcs is None:
                image_data, image_header = Hips_handler.open_hips(hips_survey)
            else:
                image_data, image_header = Hips_handler.open_hips_with_wcs(
                    hips_survey, wcs
                )
        except AttributeError:
            raise AttributeError

        self.open_image(
            image_data, image_header, hips_survey.survey, hips_survey.image_type
        )

    def close_images(self):
        if self.get_selected_image() is not None and not messagebox.askyesno(
            title="Confirmation", message=CLOSE_CONFIRM
        ):
            return

        print("Closing all images...")
        for window in self.open_windows:
            window.destroy()

        self.open_windows = []

        if self.main_image is not None:
            self.main_image.destroy()
            self.main_image = None
            self.set_selected_image(None)

        self.root.update()
        self.update_image_list_eh.invoke(None, [])

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
        if self.selected_image == image:
            return

        self.selected_image = image

        self.selected_image_eh.invoke(self.get_selected_image())

    def handle_focus(self, event):
        if self.selected_image is None:
            return

        self.set_selected_image(self.main_image)

    def close_appended_image(self, image):
        image.destroy()
        self.open_windows.remove(image)

        self.set_selected_image(self.main_image)
        self.after(1, lambda: self.root.focus_set())
        self.update_image_list_eh.invoke(self.get_selected_image(), self.get_images())
