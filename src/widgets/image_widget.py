import ttkbootstrap as tb
from astropy.io import fits
from astropy.visualization import LogStretch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# Create an Image Frame
class ImageFrame(tb.Frame):
    image_file = None

    def __init__(self, parent, file_path, x, y):
        tb.Frame.__init__(self, parent)
        self.parent = parent
        self.image_file = file_path
        self.grid(column=x, row=y, padx=10, pady=10)

        fig, ax = ImageFrame.render_fig(file_path)
        self.ax = ax

        # Embed the matplotlib figure in the tkinter window
        self.canvas = FigureCanvasTkAgg(fig, master=self)

        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(column=0, row=0)

        # Listen to mouse events
        # self.canvas.mpl_connect("scroll_event", self.zoom) # TODO this may be windows only
        self.canvas_widget.bind(
            "<MouseWheel>", self.zoom
        )  # TODO this may be windows only

    def zoom(self, event):
        # Get the current axis limits
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()

        # Calculate new axis limits based on the zoom event
        xdata = event.x  # x-coordinate of the mouse pointer
        ydata = event.y  # y-coordinate of the mouse pointer
        if xdata is None or ydata is None:
            return  # Return if no valid data

        # Define zoom factors for zooming in and out
        zoom_factor = 0.9 * (event.delta / 120)  # delta seems to be a multiple of 120
        if zoom_factor < 0:
            zoom_factor = -1 / zoom_factor

        width = current_xlim[1] - current_xlim[0]
        height = current_ylim[1] - current_ylim[0]

        new_width = width * zoom_factor
        new_height = height * zoom_factor

        # Adjust the axis limits
        new_xlim = (
            current_xlim[0] + (width - new_width) / 2,
            current_xlim[1] + (new_width - width) / 2,
        )
        new_ylim = (
            current_ylim[0] + (height - new_height) / 2,
            current_ylim[1] + (new_height - height) / 2,
        )

        # Set the new axis limits
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        # Redraw the canvas
        self.canvas.draw()

    @staticmethod
    def render_fig(image_file):
        """
        Creates the Figure object to be drawn onto the canvas.

        TODO - extract this rendering out?
        """

        # Read the .fits file
        hdu_list = fits.open(image_file)
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

        return fig, ax
