import ttkbootstrap as tb
from tkinter import filedialog

from lib.event_handler import EventHandler
from widgets import image_controller as ic
from widgets import data_controller as dc


# Create Main Tkinter Window
class MainWindow(tb.Window):
    def __init__(self):
        tb.Window.__init__(self, themename="superhero")
        self.title("FITS Image Viewer")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.menu_controller = MenuBar(self)
        self.image_controller = ic.ImageController(self)
        self.data_controller_test1 = dc.DataController(self, 0, 0, 1, 2, 50, 250)
        self.data_controller_test2 = dc.DataController(self, 2, 0, 1, 1, 50, 250)
        self.data_controller_test3 = dc.DataController(self, 1, 1, 3, 1, 250, 50)

        self.config(menu=self.menu_controller.menu)

    # Main run function for app
    # Place all functions of the app here
    def run(self):
        # Do not remove or edit, required for run loop to function
        self.update()
        self.after(100, self.run)


# Create Menu bar for tkinter window
class MenuBar(tb.Frame):
    open_file = EventHandler()

    def __init__(self, parent):
        tb.Frame.__init__(self, parent)
        self.parent = parent
        self.grid(column=0, row=0)

        self.menu = tb.Menu(self.parent)

        self.file_menu_creation()

    # Create file menu options
    def file_menu_creation(self):
        file_menu = tb.Menu(self.menu, tearoff=0)
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
