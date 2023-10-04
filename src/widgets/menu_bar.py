from tkinter import filedialog

import ttkbootstrap as tb

from src.lib.event_handler import EventHandler


# Create Menu bar for tkinter window
class MenuBar(tb.Frame):
    open_file_eh = EventHandler()
    open_image_table_eh = EventHandler()
    open_renderer_eh = EventHandler()
    append_image_eh = EventHandler()
    export_image_eh = EventHandler()
    pencil_colour_eh = EventHandler()
    pencil_size_eh = EventHandler()

    def __init__(self, parent):
        tb.Frame.__init__(self, parent)
        self.parent = parent
        self.grid(column=0, row=0)

        self.menu = tb.Menu(self.parent)

        self.file_menu_creation()
        self.widget_menu_creation()
        self.annotations_menu_creation()
        self.pencil_color = "red"  # Default color
        self.pencil_size = "small"  # Default size

    def set_pencil_color(self, color):
        self.pencil_color = color
        self.pencil_colour_eh.invoke(self.pencil_color)

    def set_pencil_size(self, size):
        self.pencil_size = size
        self.pencil_size_eh.invoke(self.pencil_size)

    # Create file menu options
    def file_menu_creation(self):
        file_menu = tb.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.open_file)
        file_menu.add_command(label="Append Image", command=self.append_image)
        file_menu.add_command(label="Export Image", command=self.export_image)
        file_menu.add_command(label="Exit", command=self.parent.quit)

    def widget_menu_creation(self):
        widget_menu = tb.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Widget", menu=widget_menu)
        widget_menu.add_command(
            label="Renderer Configuration", command=self.open_renderer
        )
        widget_menu.add_command(label="Image Table", command=self.open_image_table)

    # Create Annotations menu options
    def annotations_menu_creation(self):
        annotations_menu = tb.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Annotations", menu=annotations_menu)

        # Create a submenu for Pencil Colour
        pencil_colour_submenu = tb.Menu(annotations_menu, tearoff=0)
        annotations_menu.add_cascade(label="Pencil Colour", menu=pencil_colour_submenu)
        pencil_colour_submenu.add_command(
            label="Red", command=lambda: self.set_pencil_color("red")
        )
        pencil_colour_submenu.add_command(
            label="Blue", command=lambda: self.set_pencil_color("blue")
        )
        pencil_colour_submenu.add_command(
            label="Green", command=lambda: self.set_pencil_color("green")
        )
        pencil_colour_submenu.add_command(
            label="Black", command=lambda: self.set_pencil_color("black")
        )
        pencil_colour_submenu.add_command(
            label="White", command=lambda: self.set_pencil_color("white")
        )

        # Create a submenu for Pencil Size
        pencil_size_submenu = tb.Menu(annotations_menu, tearoff=0)
        annotations_menu.add_cascade(label="Pencil Size", menu=pencil_size_submenu)
        pencil_size_submenu.add_command(
            label="Small", command=lambda: self.set_pencil_size("1")
        )
        pencil_size_submenu.add_command(
            label="Medium", command=lambda: self.set_pencil_size("5")
        )
        pencil_size_submenu.add_command(
            label="Large", command=lambda: self.set_pencil_size("10")
        )

    # Open command for option in menu
    def open_file(self):
        file_name = filedialog.askopenfilename(
            title="Select .fits file",
            filetypes=(("Fits files", "*.fits"), ("All files", "*.*")),
        )

        if file_name == "":
            return

        self.open_file_eh.invoke(file_name)

    def open_renderer(self):
        self.open_renderer_eh.invoke()

    def open_image_table(self):
        self.open_image_table_eh.invoke()

    def append_image(self):
        file_name = filedialog.askopenfilename(
            title="Select .fits file",
            filetypes=(("Fits files", "*.fits"), ("All files", "*.*")),
        )

        if file_name == "":
            return

        self.append_image_eh.invoke(file_name)

    def export_image(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        )

        if file_path == "":
            return

        self.export_image_eh.invoke(file_path)
