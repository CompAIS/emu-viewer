import time
import tkinter as tk

import pyvips as vips
import ttkbootstrap as tb
from PIL import Image, ImageTk

import src.lib.render as Render
from src.lib.util import with_defaults


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

        self.tk_img_path = self.tk_img = self.canvas_image = None
        self.image_x = self.image_y = self.image_size = None
        self.update_canvas(file_path=file_path)

        # Listen to mouse events
        self.is_dragging = False
        self.prev_mouse_x = 0
        self.prev_mouse_y = 0

        self.canvas.bind("<Motion>", self.move)
        self.canvas.bind("<ButtonPress-1>", self.mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_up)
        self.canvas.bind("<MouseWheel>", self.zoom)
        # TODO widget changes size
        # https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
        # https://stackoverflow.com/questions/61462360/tkinter-canvas-dynamically-resize-image
        # self.canvas.bind("<Configure>", self.window_resize)

    def update_canvas(self, file_path=None, x=None, y=None, size=None):
        """
        Update canvas with image. Provide a file_path to change the image.
        Otherwise specify zoom and position arguments. TODO
        """

        start = time.time()
        self.root.update()

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        x = int(with_defaults(x, self.image_x, canvas_width / 2))
        y = int(with_defaults(y, self.image_y, canvas_height / 2))
        size = int(with_defaults(size, self.image_size, canvas_height - 20))

        # delete old image
        self.canvas.delete(self.canvas_image)

        # if we have no loaded image, or the file_path is different, load the new image
        should_reload = self.tk_img is None or (
            file_path != None and self.tk_img_path != file_path
        )

        if should_reload:
            self.tk_img_path = Render.save_file(file_path)
            self.vips_raw_img = vips.Image.new_from_file(self.tk_img_path).flatten()
            self.vips_img = self.vips_raw_img

        # resize image
        currsize = self.vips_img.width
        if size != currsize:
            resize_start = time.time()
            scale = size / self.vips_raw_img.width
            self.vips_img = self.vips_raw_img.resize(scale)
            print(f"Resize took {time.time() - resize_start}")

        if should_reload or size != currsize:
            reload_start = time.time()
            self.pil_img = Image.fromarray(self.vips_img.numpy())
            self.tk_img = ImageTk.PhotoImage(self.pil_img)
            print(f"Reload took {time.time() - resize_start} {self.pil_img.mode}")

        # draw new image
        self.canvas_image = self.canvas.create_image(x, y, image=self.tk_img)
        print(f"Rendered in {time.time() - start} (Image size: {size})")

        self.image_x = x
        self.image_y = y
        self.image_size = size

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
            width = x2 - x1
            height = y2 - y1
            x = x1 + (width / 2) + dx
            y = y1 + (height / 2) + dy

            print(f"started {x}, {y}")
            self.update_canvas(x=x, y=y)

        self.prev_mouse_x = event.x
        self.prev_mouse_y = event.y

    def zoom(self, event):
        xdata = event.x  # x-coordinate of the mouse pointer
        ydata = event.y  # y-coordinate of the mouse pointer
        if xdata is None or ydata is None:
            return  # Return if no valid data

        # Define zoom factors for zooming in and out
        zoom_factor = 0.9 if event.delta < 0 else 1 / 0.9

        new_size = self.image_size * zoom_factor

        # Redraw the canvas
        self.update_canvas(size=new_size)
