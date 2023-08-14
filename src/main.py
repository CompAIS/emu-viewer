import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog

from lib.event_handler import EventHandler
from widgets import image_controller as ic


# Create Main Tkinter Window
class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("FITS Image Viewer")
        self.geometry("250x250")

        self.menu_controller = MenuBar(self)
        self.image_controller = ic.ImageController(self)

        self.config(menu=self.menu_controller.menu)

    # Main run function for app
    # Place all functions of the app here
    def run(self):
        # Do not remove or edit, required for run loop to function
        self.update()
        self.after(100, self.run)


# Create Menu bar for tkinter window
class MenuBar(ttk.Frame):
    open_file = EventHandler()

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.grid(column=0, row=0)

        self.menu = ttk.Menu(self.parent)

        self.file_menu_creation()

    # Create file menu options
    def file_menu_creation(self):
        file_menu = ttk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open)
        file_menu.add_command(label="Exit", command=self.parent.quit)

    # Open command for option in menu
    def open(self):
        file_name = filedialog.askopenfilename(
            title="Select .fits file",
            filetypes=(("Fits files", "*.fits"), ("All files", "*.*")),
        )

        if file_name == "":
            return

        self.open_file.invoke(file_name)


if __name__ == "__main__":
    # Run the main app
    main_app = MainWindow()

    main_app.after(1000, main_app.run)

    main_app.mainloop()
