import ttkbootstrap as tb


from widgets import menu_bar as menu_bar
from widgets import tool_bar as tool_bar
import image_controller as ic
import data_controller as dc


# Create Main Tkinter Window
class MainWindow(tb.Window):
    def __init__(self):
        tb.Window.__init__(self, themename="superhero")
        self.title("FITS Image Viewer")
        self.geometry("500x500")
        self.state("zoomed")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.menu_controller = menu_bar.MenuBar(self)

        self.toolbar = tool_bar.ToolBar(self)

        self.contentWindow = ContentWindow(self)

        self.config(menu=self.menu_controller.menu)

    # Main run function for app
    # Place all functions of the app here
    def run(self):
        # Do not remove or edit, required for run loop to function
        self.update()
        self.after(100, self.run)


class ContentWindow:
    def __init__(self, parent):
        self.vertical = tb.PanedWindow(
            parent,
            orient="vertical",
            bootstyle="light",
        )
        self.vertical.grid(column=1, row=0, sticky="w" + "e" + "n" + "s")

        self.horizontal = tb.PanedWindow(
            self.vertical, orient="horizontal", bootstyle="light"
        )
        self.vertical.add(self.horizontal, weight=1)

        self.data_test_1 = dc.DataController(self.vertical, parent, 250, 50)
        self.vertical.add(self.data_test_1, weight=0)

        self.image_controller = ic.ImageController(self.horizontal, parent)
        self.horizontal.add(self.image_controller, weight=1)

        self.data_test_2 = dc.DataController(self.horizontal, parent, 250, 250)
        self.horizontal.add(self.data_test_2, weight=0)


if __name__ == "__main__":
    # Run the main app
    main_app = MainWindow()

    main_app.after(1000, main_app.run)

    main_app.mainloop()
