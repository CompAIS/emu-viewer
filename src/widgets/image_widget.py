import tkinter as tk
import warnings

import ttkbootstrap as tb
from astropy import wcs
from vispy import scene

import src.lib.render as Render
from src.controllers.widget_controller import Widget
from src.lib.match_type import MatchType

warnings.simplefilter(action="ignore", category=wcs.FITSFixedWarning)


# Create an Image Frame
class ImageFrame(tb.Frame):
    def __init__(
        self, parent, root, image_data, image_data_header, file_name, file_type
    ):
        super().__init__(parent)

        # basic layout
        self.root = root
        self.grid(column=0, row=0, padx=10, pady=10, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1, uniform="a")
        self.columnconfigure(0, weight=1, uniform="a")

        # Image data and file name
        self.image_data = image_data
        self.image_data_header = image_data_header
        self.image_wcs = None
        self.file_name = file_name
        self.file_type = file_type

        # Default render config
        self.updating = False
        self.colour_map = "inferno"
        self.stretch = "Linear"
        self.cached_percentiles = Render.get_percentiles(image_data)
        self.selected_percentile = "99.5"
        self.set_selected_percentile(self.selected_percentile)
        self.grid_lines = False

        self.matched = {match_type.value: False for match_type in MatchType}

        if self.image_data_header is not None:
            self.image_wcs = wcs.WCS(self.image_data_header).celestial
            # if self.image_wcs.world_n_dim > 2:
            #     self.image_wcs = self.image_wcs.celestial

        self.catalogue_set = None
        self.contour_levels = self.contour_set = None
        self.create_canvas()

        if file_type == "fits":
            self.image = Render.create_figure(
                self.image_data,
                self.view,
                self.image_wcs,
                self.colour_map,
                self.vmin,
                self.vmax,
                self.stretch,
                self.contour_levels,
            )

            self.vmin_line = None
            self.vmax_line = None

            min_value, max_value = self.cached_percentiles["100"]

            self.histogram = Render.create_histogram(
                self.image_data, min_value, max_value
            )

            # TODO
            # self.fig.canvas.callbacks.connect("button_press_event", self.get_ra_dec)
        else:
            # TODO
            raise NotImplementedError
            # self.fig, self.image = Render.create_figure_png(self.image_data)

        # self.canvas.draw()

    def create_canvas(self):
        self.scene_canvas = scene.SceneCanvas(
            keys="interactive", bgcolor="#2B3E50", parent=self
        )
        grid = self.scene_canvas.central_widget.add_grid()
        self.view = grid.add_view(0, 0)  # TODO tickers / axes
        self.scene_canvas.native.grid(row=0, column=0, sticky=tk.NSEW)

        # self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        # self.canvas.get_tk_widget().grid(
        #     column=0, row=0, sticky=tk.NSEW, padx=10, pady=10
        # )
        # self.canvas.draw()

        # self.toolbar = NavigationToolbar(self.canvas, self, False)
        # self.toolbar.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

        # self.toolbar.update()

    def is_matched(self, match_type: MatchType) -> bool:
        """
        Is the image currently being matched on this dimension?
        """

        return self.matched[match_type.value]

    def is_selected(self) -> bool:
        """
        Is the image that is currently selected this one?
        """

        return self.root.image_controller.get_selected_image() == self

    def toggle_match(self, match_type):
        self.matched[match_type.value] = not self.matched[match_type.value]

        if match_type == MatchType.COORD:
            # TODO implement #
            pass
        elif match_type == MatchType.RENDER:
            # TODO implement #
            pass
        elif match_type == MatchType.ANNOTATION:
            # TODO implement #
            pass

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

        self.scene_canvas.update()

    def update_colour_map(self):
        self.image = Render.update_image_cmap(self.image, self.colour_map)

        self.scene_canvas.update()

    def draw_catalogue(self, ra_coords, dec_coords, size, colour_outline, colour_fill):
        raise NotImplementedError
        # self.fig, self.catalogue_set = Render.draw_catalogue(
        #     self.fig,
        #     self.catalogue_set,
        #     ra_coords,
        #     dec_coords,
        #     size,
        #     colour_outline,
        #     colour_fill,
        # )
        # self.canvas.draw()

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
        raise NotImplementedError
        # self.contour_levels = new_contours

        # self.contour_set = Render.update_contours(
        #     self.fig,
        #     data_source,
        #     data_source_wcs,
        #     self.contour_levels,
        #     self.contour_set,
        #     gaussian_factor,
        #     line_colour,
        #     line_opacity,
        #     line_width,
        # )
        # self.canvas.draw()

    def clear_contours(self):
        self.contour_set = Render.clear_contours(self.contour_set)
        self.canvas.draw()

    def update_histogram_lines(self):
        self.histogram, self.vmin_line, self.vmax_line = Render.update_histogram_lines(
            self.histogram, self.vmin, self.vmax, self.vmin_line, self.vmax_line
        )

    def toggle_grid_lines(self):
        raise NotImplementedError
        # self.grid_lines = not self.grid_lines

        # Render.set_grid_lines(self.fig, self.grid_lines)
        # self.canvas.draw()

        # return self.grid_lines

    def get_ra_dec(self, event):
        if self.root.widget_controller.open_windows.get(Widget.HIPS_SELECT) is None:
            return

        if event.inaxes and event.inaxes.get_navigate():
            try:
                c = self.image_wcs.pixel_to_world(event.xdata, event.ydata)
                decimal = c.to_string(style="decimal", precision=5)
                coords = decimal.split()
                self.root.widget_controller.open_windows.get(
                    Widget.HIPS_SELECT
                ).set_ra_dec_entries(coords[0], coords[1])
            except (ValueError, OverflowError) as e:
                print(e)
