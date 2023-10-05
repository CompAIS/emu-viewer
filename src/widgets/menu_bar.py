from tkinter import filedialog

import ttkbootstrap as tb

from src.lib.event_handler import EventHandler
from src.widgets.hips_selector_widget import HipsSelectorWidget


# Create Menu bar for tkinter window
class MenuBar(tb.Frame):
    open_file_eh = EventHandler()
    open_image_table_eh = EventHandler()
    open_render_eh = EventHandler()
    append_image_eh = EventHandler()
    open_hips_eh = EventHandler()
    append_hips_eh = EventHandler()
    open_statistics_eh = EventHandler()

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
        file_menu.add_command(label="Open Image", command=self.open_file)
        file_menu.add_command(label="Append Image", command=self.append_image)
        file_menu.add_command(label="Open Hips Survey", command=self.open_hips)
        file_menu.add_command(label="Append Hips Survey", command=self.append_hips)
        file_menu.add_command(label="Exit", command=self.parent.quit)

    def widget_menu_creation(self):
        widget_menu = tb.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Widget", menu=widget_menu)
        widget_menu.add_command(
            label="Renderer Configuration", command=self.open_render
        )
        widget_menu.add_command(label="Statistics Table", command=self.open_statistics)
        widget_menu.add_command(label="Image Table", command=self.open_image_table)

    # Open command for option in menu
    def open_file(self):
        file_name = filedialog.askopenfilename(
            title="Select .fits file",
            filetypes=(("Fits files", "*.fits"), ("All files", "*.*")),
        )

        if file_name == "":
            return

        self.open_file_eh.invoke(file_name)

    def open_render(self):
        self.open_render_eh.invoke()

    def open_statistics(self):
        self.open_statistics_eh.invoke()

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

    def open_hips(self):
        hips_selector = HipsSelectorWidget(self, self.parent)
        self.parent.wait_window(hips_selector)

        hips_survey = hips_selector.hips_survey

        if (
            hips_survey.projection == ""
            or hips_survey.survey == ""
            or hips_survey.image_type == ""
        ):
            return

        self.open_hips_eh.invoke(hips_survey)

    def append_hips(self):
        hips_selector = HipsSelectorWidget(self, self.parent)
        self.parent.wait_window(hips_selector)

        hips_survey = hips_selector.hips_survey

        if (
            hips_survey.projection == ""
            or hips_survey.survey == ""
            or hips_survey.image_type == ""
        ):
            return

        self.append_hips_eh.invoke(hips_survey)
