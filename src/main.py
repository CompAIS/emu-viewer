import ttkbootstrap as tb

from src.controllers import image_controller as ic
from src.controllers import widget_controller as wc
from src.widgets import menu_bar as menu_bar


# Create Main Tkinter Window
class MainWindow(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("FITS Image Viewer")
        self.geometry("800x800")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.menu_controller = menu_bar.MenuBar(self)

        self.image_controller = ic.ImageController(self, self)
        self.widget_controller = wc.WidgetController(self)
        self.widget_controller.open_widget(wc.Widget.RENDERER)
        self.after(1, lambda: self.focus_set())

        self.config(menu=self.menu_controller.menu)
        self.bind("<FocusIn>", self.image_controller.handle_focus)

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
