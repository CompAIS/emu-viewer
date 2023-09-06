import ttkbootstrap as tb

from src.widgets import image_widget as iw


# Create Image Controller Frame
class ImageController(tb.Frame):
    gridX = 0
    gridY = 0

    open_images = []

    def __init__(self, parent, root):
        tb.Frame.__init__(
            self,
            parent,
            bootstyle="dark",
        )
        self.grid(
            column=1,
            row=0,
            sticky="w" + "e" + "n" + "s",
        )
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Add open_image as an event listener to open file
        root.menu_controller.open_file.add("open_image", self.open_image)

    # Open image file based on path selected
    def open_image(self, file_path):
        new_image = iw.ImageFrame(self, file_path, self.gridX, self.gridY)
        self.open_images.append(new_image)

        if self.gridX > self.gridY:
            self.gridY += 1
            self.gridX = 0
        else:
            self.gridX += 1
