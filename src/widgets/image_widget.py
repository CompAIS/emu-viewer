import tkinter as tk

import pyvips as vips
import ttkbootstrap as tb
from astropy import units as u
from astropy.wcs import WCS
from PIL import Image, ImageTk

import src.lib.render as Render
from src.lib.util import with_defaults


# Create an Image Frame
class ImageFrame(tb.Frame):
    def __init__(self, parent, root, image_data, image_data_header, file_name):
        tb.Frame.__init__(self, parent)

        # basic layout
        self.root = root
        self.parent = parent
        self.grid(column=0, row=0, padx=10, pady=10, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1, uniform="a")
        self.columnconfigure(0, weight=1, uniform="a")

        # Image data and file name
        self.image_data = image_data
        self.image_data_header = image_data_header
        self.file_name = file_name

        # Default render config
        self.colour_map = "inferno"
        self.vmin = 0.5
        self.vmax = 99.5
        self.stretch = "Linear"

        # create a tk canvas and load initial image
        self.canvas = tk.Canvas(master=self)
        self.canvas.grid(column=0, row=0, sticky=tk.NSEW)

        self.tk_img_path = self.tk_img = None
        self.cx = self.cy = self.csize = None

        self.updating = False
        self.canvas_image = self.canvas.create_image(0, 0, image=None)

        self.create_image_render()
        self.update_canvas()

        # image info label
        self.image_info = self.canvas.create_text(0, 0, text="", fill="white")
        self.canvas.tag_raise(self.image_info)

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

    # We have three different "coordinate" systems here
    # - (c) on the actual canvas (between 0 and the canvas_width/height)
    # - (r) on the *raw* image (before scaling)
    # - (s) on the *scaled* image

    def update_canvas(self, update_image=False, cx=None, cy=None, csize=None):
        """
        Update canvas with image. Provide a file_path to change the image.
        Otherwise specify zoom and position arguments. TODO
        """

        # Some assumptions:
        # - aspect ratio is always 1:1 for the image, so we can use 'width' to mean 'size'

        if self.updating:
            return

        self.updating = True

        try:
            self.root.update()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            cx = self.cx = with_defaults(cx, self.cx, canvas_width / 2)
            cy = self.cy = with_defaults(cy, self.cy, canvas_height / 2)
            self.csize = with_defaults(csize, self.csize, canvas_height - 20)
            csize_desired = int(self.csize)

            # (desired) bounding box of the image on the canvas
            cx1, cx2, cy1, cy2 = (
                cx - csize_desired / 2,
                cx + csize_desired / 2,
                cy - csize_desired / 2,
                cy + csize_desired / 2,
            )

            # if we have no loaded image, or the file_path is different, render the image
            should_reload = self.tk_img is None or update_image

            if should_reload:
                self.vips_raw_img = vips.Image.new_from_file(self.tk_img_path).flatten()
                self.vips_resized_img = self.vips_raw_img

            # resize image if the given size is different from our current
            csize_prev = self.vips_resized_img.width
            if csize_desired != csize_prev:
                scale_rs = csize_desired / self.vips_raw_img.width
                self.vips_resized_img = self.vips_raw_img.resize(scale_rs)

            # reload image if we made any changes
            if should_reload or csize_desired != csize_prev:
                self.pil_img = Image.fromarray(self.vips_resized_img.numpy())
                self.tk_img = ImageTk.PhotoImage(self.pil_img)

            # load new image in
            self.canvas.itemconfig(self.canvas_image, image=self.tk_img)
            self.canvas.moveto(self.canvas_image, cx1, cy1)
        except Exception as e:
            print(e)

        self.updating = False

    def create_image_render(self):
        self.tk_img_path = Render.create_render(
            self.image_data, self.colour_map, self.vmin, self.vmax, self.stretch
        )

    def update_image_render(self):
        self.tk_img_path = Render.create_render(
            self.image_data, self.colour_map, self.vmin, self.vmax, self.stretch
        )
        self.update_canvas(update_image=True)

    def mouse_down(self, event):
        self.is_dragging = True
        self.prev_mouse_x = event.x
        self.prev_mouse_y = event.y

    def mouse_up(self, event):
        self.is_dragging = False

    def move(self, event):
        x1, y1, x2, y2 = self.canvas.bbox(self.canvas_image)
        width = x2 - x1
        height = y2 - y1

        if self.is_dragging:
            dx = event.x - self.prev_mouse_x
            dy = event.y - self.prev_mouse_y

            x = x1 + (width / 2) + dx
            y = y1 + (height / 2) + dy

            self.update_canvas(cx=x, cy=y)
        # converts values on the canvas to the corresponding values on the raw image
        scale_cr = self.vips_raw_img.width / self.csize
        rx_image = (event.x - x1) * scale_cr
        ry_image = (height - (event.y - y1)) * scale_cr

        # update text
        fx_image, fy_image = self.r_to_fits_coordinate(rx_image, ry_image)

        if self.image_data_header is not None:
            w = WCS(self.image_data_header)

            c = w.pixel_to_world(fx_image, fy_image)

            # The units here match CARTA. Don't know why.
            ra = c.ra.to_string(unit=u.hour, sep=":", pad=True, precision=2)
            dec = c.dec.to_string(unit=u.degree, sep=":", pad=True, precision=2)

            self.canvas.itemconfig(
                self.image_info,
                text=f"WCS: ({ra}, {dec}); Image: ({int(fx_image)}, {int(fy_image)});",
            )

        self.canvas.moveto(self.image_info, 10, 10)

        self.prev_mouse_x = event.x
        self.prev_mouse_y = event.y

    def r_to_fits_coordinate(self, rx_image, ry_image):
        width, height = self.image_data.shape
        return (
            rx_image * width / self.vips_raw_img.width,
            ry_image * height / self.vips_raw_img.height,
        )

    def zoom(self, event):
        cx_mouse = event.x
        cy_mouse = event.y
        if cx_mouse is None or cy_mouse is None:
            return

        zoom_factor = 0.9 if event.delta < 0 else 1 / 0.9

        new_size = self.csize * zoom_factor

        # Redraw the canvas
        # TODO should zoom into mouse
        self.update_canvas(csize=new_size)
