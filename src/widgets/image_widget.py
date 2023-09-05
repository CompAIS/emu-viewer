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

        self.tk_img_path = self.tk_img = None
        self.cx = self.cy = self.csize = None
        self.updating = False
        self.canvas_image = self.canvas.create_image(0, 0, image=None)
        self.update_canvas(file_path=file_path)

        # image info label
        self.image_info = tb.Label(self, text="")
        self.image_info.grid(column=0, row=0, sticky=tk.N + tk.EW)

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

    def update_canvas(self, file_path=None, cx=None, cy=None, csize=None):
        """
        Update canvas with image. Provide a file_path to change the image.
        Otherwise specify zoom and position arguments. TODO
        """

        # Some assumptions:
        # - aspect ratio is always 1:1 for the image, so we can use 'width' to mean 'size'

        print(f"updating: {self.updating}")
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
            print(f"RENDER: {cx, cy, csize_desired}")

            # (desired) bounding box of the image on the canvas
            cx1, cx2, cy1, cy2 = (
                cx - csize_desired / 2,
                cx + csize_desired / 2,
                cy - csize_desired / 2,
                cy + csize_desired / 2,
            )

            # if we have no loaded image, or the file_path is different, render the image
            should_reload = self.tk_img is None or (
                file_path != None and self.tk_img_path != file_path
            )

            if should_reload:
                self.tk_img_path = Render.save_file(file_path)
                self.vips_raw_img = vips.Image.new_from_file(self.tk_img_path).flatten()
                self.vips_cropped_img = self.vips_resized_img = self.vips_raw_img

            # resize image if the given size is different from our current
            csize_prev = self.vips_resized_img.width
            if csize_desired != csize_prev:
                scale_rs = csize_desired / self.vips_raw_img.width
                self.vips_resized_img = self.vips_raw_img.resize(scale_rs)
                self.vips_cropped_img = self.vips_resized_img

            # if any portion of the image is off-screen, we should crop it out
            is_oob = cx1 < 0 or cy1 < 0 or cx2 > canvas_width or cy2 > canvas_height
            sx1, sy1 = max(0, -cx1), max(0, -cy1)
            swidth, sheight = min(csize_desired, cx2), min(csize_desired, cy2)
            if is_oob:
                if swidth > 0 and sheight > 0:
                    self.vips_cropped_img = self.vips_resized_img.crop(
                        sx1, sy1, swidth, sheight
                    )

            # reload image if we made any changes
            if should_reload or csize_desired != csize_prev or is_oob:
                self.pil_img = Image.fromarray(self.vips_cropped_img.numpy())
                self.tk_img = ImageTk.PhotoImage(self.pil_img)
                # reload_start = time.time()
                # print(f"Step 1: took {time.time() - reload_start} {self.pil_img.mode}")
                # print(f"Reload took {time.time() - reload_start} {self.pil_img.mode}")

            # load new image in
            self.canvas.itemconfig(self.canvas_image, image=self.tk_img)
            self.canvas.moveto(self.canvas_image, cx1 + sx1, cy1 + sy1)
            # print(f"Rendered in {time.time() - start} (Image size: {csize_desired})")

        except Exception as e:
            print(e)

        self.updating = False

    def mouse_down(self, event):
        self.is_dragging = True
        self.prev_mouse_x = event.x
        self.prev_mouse_y = event.y

    def mouse_up(self, event):
        self.is_dragging = False

    def move(self, event):
        x1, y1, x2, y2 = self.canvas.bbox(self.canvas_image)
        if self.is_dragging:
            dx = event.x - self.prev_mouse_x
            dy = event.y - self.prev_mouse_y

            width = x2 - x1
            height = y2 - y1
            x = x1 + (width / 2) + dx
            y = y1 + (height / 2) + dy

            print(f"MOVE: {x, y}")
            self.update_canvas(cx=x, cy=y)
        else:
            self.image_info.configure(text=f"Image: ({event.x - x1}, {event.y - y1})")

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
        # TODO should zoom into mouse
        self.update_canvas(csize=new_size)
