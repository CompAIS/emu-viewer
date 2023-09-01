import ttkbootstrap as tb
from astropy.io import fits
from astropy.visualization import LogStretch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# Create an Image Frame
class ImageFrame(tb.Frame):
    image_file = None
    is_dragging = False
    prev_mouse_x = 0
    prev_mouse_y = 0

    def __init__(self, parent, file_path, x, y):
        tb.Frame.__init__(self, parent)
        self.parent = parent
        self.image_file = file_path
        self.grid(column=x, row=y, padx=10, pady=10)
        self.grid_rowconfigure(x, weight=1)
        self.grid_columnconfigure(y, weight=1)

        fig, ax = ImageFrame.render_fig(file_path)
        self.fig = fig
        self.ax = ax

        # Embed the matplotlib figure in the tkinter window
        self.canvas = FigureCanvasTkAgg(fig, master=self)

        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(column=0, row=0)

        # Listen to mouse events
        self.canvas_widget.bind("<MouseWheel>", self.zoom)
        self.canvas_widget.bind("<ButtonPress-1>", self.mouse_down)
        self.canvas_widget.bind("<ButtonRelease-1>", self.mouse_up)
        self.canvas_widget.bind("<Motion>", self.move)

    def mouse_down(self, event):
        self.is_dragging = True
        self.prev_mouse_x = event.x
        self.prev_mouse_y = event.y

    def mouse_up(self, event):
        self.is_dragging = False

    def move(self, event):
        if self.is_dragging:
            figwidth = self.fig.get_figwidth() * self.fig.dpi
            figheight = self.fig.get_figheight() * self.fig.dpi
            current_xlim = self.ax.get_xlim()
            current_ylim = self.ax.get_ylim()

            dx = event.x - self.prev_mouse_x
            dy = event.y - self.prev_mouse_y
            x_ratio = dx / figwidth
            y_ratio = dy / figheight

            width = current_xlim[1] - current_xlim[0]
            height = current_ylim[1] - current_ylim[0]

            new_xlim = (
                current_xlim[0] - x_ratio * width,
                current_xlim[1] - x_ratio * width,
            )
            new_ylim = (
                current_ylim[0] + y_ratio * height,
                current_ylim[1] + y_ratio * height,
            )

            # Set the new axis limits
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)

            # Redraw the canvas
            self.canvas.draw()

        self.prev_mouse_x = event.x
        self.prev_mouse_y = event.y

    def zoom(self, event):
        figwidth = self.fig.get_figwidth() * self.fig.dpi
        figheight = self.fig.get_figheight() * self.fig.dpi
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()

        # Calculate new axis limits based on the zoom event
        xdata = event.x  # x-coordinate of the mouse pointer
        ydata = event.y  # y-coordinate of the mouse pointer
        if xdata is None or ydata is None:
            return  # Return if no valid data

        # Define zoom factors for zooming in and out
        zoom_factor = 0.9 if event.delta > 0 else 1 / 0.9

        width = current_xlim[1] - current_xlim[0]
        height = current_ylim[1] - current_ylim[0]

        new_width = width * zoom_factor
        new_height = height * zoom_factor

        dwidth = width - new_width
        dheight = height - new_height

        x_ratio = xdata / figwidth
        x_left = x_ratio * dwidth
        x_right = -(1 - x_ratio) * dwidth

        # I have no idea why this is flipped
        y_ratio = ydata / figheight
        y_left = (1 - y_ratio) * dheight
        y_right = -y_ratio * dheight

        new_xlim = (
            current_xlim[0] + x_left,
            current_xlim[1] + x_right,
        )
        new_ylim = (
            current_ylim[0] + y_left,
            current_ylim[1] + y_right,
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
        fig = Figure(figsize=(5, 5), dpi=150)
        ax = fig.add_subplot()
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        ax.margins(0, 0)
        ax.axis("off")

        # Render the scaled image data onto the figure
        cax = ax.imshow(scaled_data, origin="lower")

        return fig, ax
