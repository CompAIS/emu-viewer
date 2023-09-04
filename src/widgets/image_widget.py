import tkinter as tk

import ttkbootstrap as tb
from PIL import ImageTk

import src.lib.render as Render


# Create an Image Frame
class ImageFrame(tb.Frame):
    def __init__(self, parent, root, file_path, x, y):
        tb.Frame.__init__(self, parent)

        # basic layout
        self.root = root
        self.parent = parent
        self.grid(column=x, row=y, padx=10, pady=10, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1, uniform="a")
        self.columnconfigure(0, weight=1, uniform="a")

        # create a tk canvas and load initial image
        self.canvas = tk.Canvas(master=self)
        self.canvas.grid(column=0, row=0, sticky=tk.NSEW)

        self.tk_img_path = None
        self.tk_img = None
        self.canvas_image = None
        self.update_canvas(file_path=file_path)

        # Listen to mouse events
        self.is_dragging = False
        self.prev_mouse_x = 0
        self.prev_mouse_y = 0

        # self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_up)
        self.canvas.bind("<Motion>", self.move)
        # TODO widget changes size
        # https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
        # https://stackoverflow.com/questions/61462360/tkinter-canvas-dynamically-resize-image
        # self.canvas.bind("<Configure>", self.window_resize)

    def update_canvas(self, file_path=None, x=None, y=None):
        """
        Update canvas with image. Provide a file_path to change the image.
        Otherwise specify zoom and position arguments. TODO
        """

        self.root.update()
        if x is None:
            x = self.canvas.winfo_width() / 2

        if y is None:
            y = self.canvas.winfo_height() / 2

        # delete old image
        self.canvas.delete(self.canvas_image)

        # if we have no loaded image, or the file_path is different, load the new image
        if self.tk_img == None or (file_path != None and self.tk_img_path != file_path):
            # load new image
            self.tk_img_path = Render.save_file(file_path)
            self.tk_img = ImageTk.PhotoImage(file=self.tk_img_path)

        # draw new image
        self.canvas_image = self.canvas.create_image(x, y, image=self.tk_img)

    def mouse_down(self, event):
        self.is_dragging = True
        self.prev_mouse_x = event.x
        self.prev_mouse_y = event.y

    def mouse_up(self, event):
        self.is_dragging = False

    def move(self, event):
        if self.is_dragging:
            dx = event.x - self.prev_mouse_x
            dy = event.y - self.prev_mouse_y

            x1, y1, x2, y2 = self.canvas.bbox(self.canvas_image)
            x = x1 + ((x2 - x1) / 2) + dx
            y = y1 + ((y2 - y1) / 2) + dy

            self.update_canvas(x=x, y=y)

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
