from tkinter import filedialog

import ttkbootstrap as tb

from src.lib.event_handler import EventHandler


# Create Menu bar for tkinter window
class MenuBar(tb.Frame):
    open_file = EventHandler()

    def __init__(self, parent):
        tb.Frame.__init__(self, parent)
        self.parent = parent
        self.grid(column=0, row=0)

        self.menu = tb.Menu(self.parent)

        self.file_menu_creation()
        self.widget_menu_creation()

    # Create file menu options
    def file_menu_creation(self):
        file_menu = tb.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open)
        file_menu.add_command(label="Exit", command=self.parent.quit)

    def widget_menu_creation(self):
        widget_menu = tb.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Widget", menu=widget_menu)
        widget_menu.add_command(label="Histogram", command=self.open_histogram)
        widget_menu.add_command(label="Image Table", command=self.open_image_table)

    # Open command for option in menu
    def open(self):
        file_name = filedialog.askopenfilename(
            title="Select .fits file",
            filetypes=(("Fits files", "*.fits"), ("All files", "*.*")),
        )

        if file_name == "":
            return

        self.open_file.invoke("open_image", file_name)

    def open_histogram(self):
        self.open_file.invoke("open_histogram_widget")

    def open_image_table(self):
        self.open_file.invoke("open_image_table_widget")
