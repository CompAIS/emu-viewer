import tkinter as tk
import warnings

import ttkbootstrap as tb
from astropy import wcs
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import src.lib.render as Render

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

        self.image_wcs = wcs.WCS(self.image_data_header)
        self.fig, self.cbar = Render.create_figure(
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
        self.canvas.get_tk_widget().grid(column=0, row=0, sticky=tk.NSEW)
        self.canvas.draw()

        self.toolbar = NavigationToolbar2Tk(
            self.canvas, self.parent, pack_toolbar=False
        )
        self.toolbar.grid(column=0, row=1, sticky=tk.NSEW)
        self.toolbar.update()

    def update_image(self):
        self.fig, self.cbar = Render.update_figure(
            self.fig,
            self.cbar,
            self.image_data,
            self.colour_map,
            self.vmin,
            self.vmax,
            self.stretch,
        )
        self.canvas.draw()
