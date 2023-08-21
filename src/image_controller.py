import ttkbootstrap as tb
from astropy.io import fits
from astropy.visualization import LogStretch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


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

        # Add open_image as an event listener to open file
        root.menu_controller.open_file.add(self.open_image)

    # Open image file based on path selected
    def open_image(self, file_path):
        new_image = ImageFrame(self, file_path, self.gridX, self.gridY)
        self.open_images.append(new_image)

        if self.gridX > self.gridY:
            self.gridY += 1
            self.gridX = 0
        else:
            self.gridX += 1


# Create an Image Frame
class ImageFrame(tb.Frame):
    image_file = None

    def __init__(self, parent, file_path, x, y):
        tb.Frame.__init__(self, parent)
        self.parent = parent
        self.image_file = file_path
        self.grid(column=x, row=y, padx=10, pady=10)
        self.handle_image()

    def handle_image(self):
        # Read the .fits file
        hdu_list = fits.open(self.image_file)
        image_data = hdu_list[0].data

        # Apply logarithmic scaling to the image data
        log_stretch = LogStretch()
        scaled_data = log_stretch(image_data)

        # Create a matplotlib figure
        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot()
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        ax.margins(0, 0)
        ax.axis("off")

        # Render the scaled image data onto the figure
        cax = ax.imshow(scaled_data, cmap="gray", origin="lower")

        # Embed the matplotlib figure in the tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0, row=0)
