import multiprocessing
import sys
import tkinter as tk

import ttkbootstrap as tb

import src.constants as constants
import src.controllers.image_controller as ic
import src.controllers.widget_controller as wc
import src.widgets.menu_bar as menu_bar


# Create Main Tkinter Window
class MainWindow(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        constants.load_images()  # load all images once tk is up

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

        # TODO refactor widget controller
        self.widget_controller = wc.WidgetController(self)
        self.widget_controller.open_widget(wc.Widget.RENDERER)
        self.after(1, lambda: self.focus_set())

        self.config(menu=self.menu_controller.menu)
        self.bind("<FocusIn>", self.handle_focus)
        self.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

        ic.register_main(self)

    def run(self):
        """Run loop for the main window.

        Updates the window every 100ms.
        """
        # TODO do we need all this

        # Do not remove or edit, required for run loop to function
        # self.update()
        # self.after(100, self.run)

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

    main_app.after(1000, main_app.run)

    main_app.mainloop()
