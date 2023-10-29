import multiprocessing
import sys
import tkinter as tk

import ttkbootstrap as tb

import src.components.menu_bar as menu_bar
import src.constants as constants
from src.controllers import image_controller as ic
from src.controllers import widget_controller as wc


# Create Main Tkinter Window
class MainWindow(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        constants.load_images()  # load all images once tk is up
        ic.register_main(self)
        wc.register_main(self)

        self.title("EMU Viewer")
        self.iconphoto(True, constants.ICONPNG)
        self.iconbitmap(constants.FAVICON_PATH)  # windows title icon
        self.geometry("800x800")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.menu_controller = menu_bar.MenuBar(self)

        self.main_image_container = tb.Frame(self, bootstyle="dark")
        self.main_image_container.grid(column=1, row=0, sticky=tk.NSEW)
        self.main_image_container.rowconfigure(0, weight=1)
        self.main_image_container.columnconfigure(0, weight=1)

        self.main_image = None

        wc.open_widget(wc.Widget.RENDERER)
        self.after(1, lambda: self.focus_set())

        self.config(menu=self.menu_controller.menu)
        self.bind("<FocusIn>", self.handle_focus)
        self.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

    def handle_focus(self, event):
        """Event listener for <FocusIn> on the main window.

        Should set the selected image to the main image.
        """
        ic.set_selected_image(self.main_image)


if __name__ == "__main__":
    # Pyinstaller fix https://stackoverflow.com/a/32677108
    multiprocessing.freeze_support()

    # Run the main app
    main_app = MainWindow()

    main_app.mainloop()
