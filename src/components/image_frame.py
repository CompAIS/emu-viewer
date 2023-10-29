import tkinter as tk
import warnings
from typing import Optional

import numpy.typing as npt
import ttkbootstrap as tb
from astropy import wcs
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import src.lib.render as Render
from src.controllers import image_controller as ic
from src.controllers import widget_controller as wc
from src.enums import DataType, Matching
from src.lib.tool import NavigationToolbar
from src.lib.util import index_default

warnings.simplefilter(action="ignore", category=wcs.FITSFixedWarning)


class ImageFrame(tb.Frame):
    """The frame containing the matplotlib plot and the toolbar."""

    def __init__(
        self,
        parent: tk.Widget,
        root: tb.Window,
        image_data: npt.ArrayLike,
        image_data_header,  # TODO type?
        file_name: str,
        data_type: DataType,
    ):
        """Construct an ImageFrame.

        :param parent: the parent widget of this image frame.
            In practice, this is either a StandaloneImage or the MainWindow.
        :param root: the main window
        :param image_data: numpy array with the image's data (fits image or png image). Note that this should
            be float[][].
        :param image_data_header: HDU header for the .fits file. None for png/jpg.
        :param file_name: the name of the file where the data came from. HiPs survey name for hips
        :param data_type: The type of the data in image_data.
        """

        super().__init__(parent)

        # basic layout
        self.root = root
        self.grid(column=0, row=0, padx=10, pady=10, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1, uniform="a")
        self.columnconfigure(0, weight=1, uniform="a")

        # Image data and file name
        self.image_data = image_data
        self.image_data_header = image_data_header
        self.image_wcs: Optional[wcs.WCS] = None
        self.file_name = file_name
        self.data_type = data_type

        # Default render config
        self.colour_map = "inferno"
        self.stretch = "Linear"
        self.cached_percentiles = Render.get_percentiles(image_data)
        self.selected_percentile = "99.5"
        self.set_selected_percentile(self.selected_percentile)
        self.grid_lines = False

        self.matched = {Matching.value: False for Matching in Matching}

        if self.image_data_header is not None:
            self.image_wcs = wcs.WCS(self.image_data_header).celestial

        self.catalogue_set = None
        self.contour_levels = self.contour_set = None
        if data_type == DataType.FITS:
            self.fig, self.image, self.limits = Render.create_figure(
                self.image_data,
                self.image_wcs,
                self.colour_map,
                self.vmin,
                self.vmax,
                self.stretch,
                self.contour_levels,
            )

            self.original_limits = self.limits

            self.vmin_line = None
            self.vmax_line = None

            min_value, max_value = self.cached_percentiles["100"]

            self.histo_counts, self.histo_bins = Render.create_histogram_data(
                self.image_data, min_value, max_value
            )

            self.fig.canvas.mpl_connect("button_press_event", self.on_click)
            self.coord_matching_cid = None
        else:
            self.fig, self.image = Render.create_figure_png(self.image_data)

        self.create_image()

    def create_image(self):
        """Handles the creation of the base matplotlib canvas and the
        associated toolbar.
        """
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(
            column=0, row=0, sticky=tk.NSEW, padx=10, pady=10
        )
        self.canvas.draw()

        self.toolbar = NavigationToolbar(self.canvas, self, False)
        self.toolbar.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

        self.toolbar.update()

    def is_matched(self, Matching: Matching) -> bool:
        """Is the image currently being matched on this dimension?"""

        return self.matched[Matching.value]

    def is_selected(self) -> bool:
        """Is the image that is currently selected this one?"""

        return ic.get_selected_image() == self

    def toggle_match(self, Matching: Matching):
        """Toggles whether or not this image is matching on the given matching.

        :param matching: the matching to toggle this image on
        """

        # are we matching or unmatching
        is_matching = not self.matched[Matching.value]

        if Matching == Matching.COORD:
            if is_matching:
                self.limits = Render.get_limits(self.fig, self.image_wcs)
                # update our current limits + watch for when our limits change
                limits = ic.get_coord_matched_limits(self)
                self.set_limits(limits)
                self.add_coords_event()
            else:
                self.set_limits(self.original_limits)
                self.remove_coords_event()
        elif Matching == Matching.RENDER:
            if is_matching:
                self.match_render()
        elif Matching == Matching.ANNOTATION:
            # TODO implement #
            pass

        # then update our matching status
        self.matched[Matching.value] = is_matching
        self.root.update()

    def set_vmin_vmax_custom(self, vmin, vmax):
        if (vmin, vmax) == (self.vmin, self.vmax):
            return

        self.vmin = vmin
        self.vmax = vmax
        self.selected_percentile = "Custom"

    def set_selected_percentile(self, percentile):
        self.selected_percentile = percentile

        if percentile == "Custom":
            return

        self.vmin, self.vmax = self.cached_percentiles[self.selected_percentile]

    def set_scaling(self, scaling):
        self.stretch = scaling

    def set_colour_map(self, colour_map):
        self.colour_map = colour_map

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

    def match_render(self, source_image=None):
        if source_image is None:
            source_image = index_default(
                ic.get_images_matched_to(Matching.RENDER),
                0,
                self,
            )
            if source_image == self:
                return

        self.set_colour_map(source_image.colour_map)
        self.update_colour_map()
        self.set_scaling(source_image.stretch)
        self.set_vmin_vmax_custom(source_image.vmin, source_image.vmax)
        self.update_norm()

    def draw_catalogue(self, ra_coords, dec_coords, size, colour_outline, colour_fill):
        self.fig, self.catalogue_set = Render.draw_catalogue(
            self.fig,
            self.catalogue_set,
            ra_coords,
            dec_coords,
            size,
            colour_outline,
            colour_fill,
        )
        self.canvas.draw()

    def reset_catalogue(self):
        self.catalogue_set = Render.reset_catalogue(self.catalogue_set)
        self.canvas.draw()

    def update_contours(
        self,
        data_source,
        data_source_wcs,
        new_contours,
        gaussian_factor,
        line_colour,
        line_opacity,
        line_width,
    ):
        self.contour_levels = new_contours

        self.contour_set = Render.update_contours(
            self.fig,
            data_source,
            data_source_wcs,
            self.contour_levels,
            self.contour_set,
            gaussian_factor,
            line_colour,
            line_opacity,
            line_width,
        )
        self.canvas.draw()

    def clear_contours(self):
        self.contour_set = Render.clear_contours(self.contour_set)
        self.canvas.draw()

    def set_limits(self, limits):
        if not self.data_type == DataType.FITS:
            return

        self.limits = limits
        self.toolbar.update_stack()

        self.fig = Render.set_limits(self.fig, self.image_wcs, self.limits)
        self.canvas.draw()

    def add_coords_event(self):
        self.coord_matching_cid = self.fig.canvas.callbacks.connect(
            "button_release_event", self.on_lims_change
        )

    def remove_coords_event(self):
        self.fig.canvas.callbacks.disconnect(self.coord_matching_cid)

    def on_lims_change(self, event):
        if (
            self.fig.canvas.toolbar.mode == "pan/zoom"
            or self.fig.canvas.toolbar.mode == "zoom rect"
        ):
            self.update_matched_images()

    def update_matched_images(self):
        self.limits = Render.get_limits(self.fig, self.image_wcs)

        for image in ic.get_images_matched_to(Matching.COORD):
            if image == self:
                continue

            image.set_limits(self.limits)

    def toggle_grid_lines(self):
        self.grid_lines = not self.grid_lines

        Render.set_grid_lines(self.fig, self.grid_lines)
        self.canvas.draw()

        return self.grid_lines

    def on_click(self, event):
        if self.fig.canvas.toolbar.mode != "" or self.data_type != DataType.FITS:
            return

        # this is a matplotlib event, so we don't have the access to the x/y for the context menu position
        # (the pointer)
        # so grab it manually
        window_x, window_y = (
            self.canvas.get_tk_widget().winfo_pointerx(),
            self.canvas.get_tk_widget().winfo_pointery(),
        )

        ax = self.fig.axes[0]
        if ax == event.inaxes and event.button == 3:
            # transform from position on the canvas to image position
            image_x, image_y = ax.transData.inverted().transform((event.x, event.y))

            self.show_context_menu(
                event,
                round(image_x),
                round(image_y),
                window_x,
                window_y,
                self.image_data[round(image_y)][round(image_x)],
            )

    def show_context_menu(self, event, image_x, image_y, window_x, window_y, value):
        self.context_menu = ImageContextMenu(self, image_x, image_y, value)
        self.context_menu.post(window_x, window_y)


class ImageContextMenu(tk.Menu):
    def __init__(self, image_frame, xdata, ydata, value):
        super().__init__(image_frame, tearoff=0)
        self.image_frame = image_frame
        self.xdata = xdata
        self.ydata = ydata
        self.coord = image_frame.image_wcs.pixel_to_world(xdata, ydata)
        self.value = value

        self.add_command(
            label="Copy WCS Coords (Decimal)", command=self.copy_decimal_coords
        )
        self.add_command(
            label="Copy WCS Coords (HMSDMS)", command=self.copy_hmsdms_coords
        )
        self.add_command(label="Copy Image Coords", command=self.copy_image_coords)
        self.add_command(label="Copy Value at Coords", command=self.copy_coord_value)
        self.add_separator()
        self.add_command(
            label="Set RA/DEC in HiPs Survey Selector", command=self.set_ra_dec
        )

    def copy_decimal_coords(self):
        decimal = self.coord.to_string(style="decimal").replace(" ", ", ")
        self.copy_to_clipboard(f"WCS: ({decimal})")

    def copy_hmsdms_coords(self):
        hmsdms = self.coord.to_string(style="hmsdms", sep=":", pad=True).replace(
            " ", ", "
        )
        self.copy_to_clipboard(f"WCS: ({hmsdms})")

    def copy_image_coords(self):
        self.copy_to_clipboard(f"Image: ({self.xdata}, {self.ydata})")

    def copy_coord_value(self):
        self.copy_to_clipboard(str(self.value))

    def copy_to_clipboard(self, text):
        self.image_frame.clipboard_clear()
        self.image_frame.clipboard_append(text)
        self.image_frame.update()

    def set_ra_dec(self):
        wc.open_widget(wc.Widget.HIPS_SELECT)

        decimal = self.coord.to_string(style="decimal")
        coords = decimal.split()
        wc.get_widget(wc.Widget.HIPS_SELECT).set_ra_dec_entries(coords[0], coords[1])
