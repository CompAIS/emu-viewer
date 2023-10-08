import tkinter as tk
import warnings

import ttkbootstrap as tb
from astropy import wcs
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import src.lib.render as Render
from src.lib.tool import NavigationToolbar

warnings.simplefilter(action="ignore", category=wcs.FITSFixedWarning)


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
        self.updating = False
        self.colour_map = "inferno"
        self.vmin = 0.5
        self.vmax = 99.5
        self.stretch = "Linear"

        self.catalogue_set = None

        self.image_wcs = wcs.WCS(self.image_data_header)
        if self.image_wcs.world_n_dim > 2:
            self.image_wcs = self.image_wcs.celestial

        self.fig, self.image = Render.create_figure(
            self.image_data,
            self.image_wcs,
            self.colour_map,
            self.vmin,
            self.vmax,
            self.stretch,
        )

        self.create_image()

    def create_image(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.get_tk_widget().grid(
            column=0, row=0, sticky=tk.NSEW, padx=10, pady=10
        )
        self.canvas.draw()

        self.toolbar = NavigationToolbar(self.canvas, self.parent, False)
        self.toolbar.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

        self.toolbar.update()

    def update_norm(self):
        self.image = Render.update_image_norm(
            self.image,
            self.image_data,
            self.vmin,
            self.vmax,
            self.stretch,
        )
        self.canvas.draw()

    def update_colour_map(self):
        self.image = Render.update_image_cmap(self.image, self.colour_map)
        self.canvas.draw()

    def draw_catalogue(self, ra_coords, dec_coords):
        self.fig, self.catalogue_set = Render.draw_catalogue(
            self.fig, ra_coords, dec_coords
        )
        self.canvas.draw()

    def reset_catalogue(self):
        self.fig, self.catalogue_set = Render.reset_catalogue(
            self.fig, self.catalogue_set
        )
        self.canvas.draw()
