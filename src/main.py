import ttkbootstrap as tb

from src.controllers import image_controller as ic
from src.controllers import widget_controller as wc
from src.widgets import menu_bar as menu_bar
from src.widgets import tool_bar as tool_bar


# Create Main Tkinter Window
class MainWindow(tb.Window):
    def __init__(self):
        tb.Window.__init__(self, themename="superhero")
        self.title("FITS Image Viewer")
        self.geometry("500x500")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.menu_controller = menu_bar.MenuBar(self)

        self.toolbar = tool_bar.ToolBar(self)

        self.image_controller = ic.ImageController(self, self)
        self.widget_controller = wc.WidgetController(self)

        self.config(menu=self.menu_controller.menu)

    # Main run function for app
    # Place all functions of the app here
    def run(self):
        # Do not remove or edit, required for run loop to function
        self.update()
        self.after(100, self.run)


if __name__ == "__main__":
    # Run the main app
    main_app = MainWindow()

    main_app.after(1000, main_app.run)

    main_app.mainloop()
