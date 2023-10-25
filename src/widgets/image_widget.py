import tkinter as tk
import warnings

import ttkbootstrap as tb
from astropy import wcs
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import src.lib.render as Render
from src.controllers.widget_controller import Widget
from src.lib.match_type import MatchType
from src.lib.tool import NavigationToolbar
from src.lib.util import index_default

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

        self.matched = {match_type.value: False for match_type in MatchType}

        if self.image_data_header is not None:
            self.image_wcs = wcs.WCS(self.image_data_header).celestial
            # if self.image_wcs.world_n_dim > 2:
            #     self.image_wcs = self.image_wcs.celestial

        self.catalogue_set = None
        self.contour_levels = self.contour_set = None
        if file_type == "fits":
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

            # self.fig.canvas.callbacks.connect(
            #     "button_release_event", self.on_lims_change
            # )
            self.fig.canvas.callbacks.connect("button_press_event", self.get_ra_dec)
            self.coord_matching_cid = None
        else:
            self.fig, self.image = Render.create_figure_png(self.image_data)

        self.create_image()
        self.canvas.draw()

    def create_image(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.context_menu = ImageContextMenu(self, self)
        self.canvas.get_tk_widget().grid(
            column=0, row=0, sticky=tk.NSEW, padx=10, pady=10
        )
        self.canvas.draw()

        self.toolbar = NavigationToolbar(self.canvas, self, False)
        self.toolbar.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

        self.toolbar.update()

        # Bind right-click event to show the context menu
        if self.image:
            self.canvas.get_tk_widget().bind("<Button-3>", self.on_right_click)

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
        # are we matching or unmatching
        is_matching = not self.matched[match_type.value]

        if match_type == MatchType.COORD:
            if is_matching:
                self.limits = Render.get_limits(self.fig, self.image_wcs)
                # update our current limits + watch for when our limits change
                limits = self.root.image_controller.get_coord_matched_limits(
                    self
                ).limits
                self.set_limits(limits)
                self.add_coords_event()
            else:
                self.set_limits(self.original_limits)
                self.remove_coords_event()
        elif match_type == MatchType.RENDER:
            if is_matching:
                self.match_render()
        elif match_type == MatchType.ANNOTATION:
            # TODO implement #
            pass

        # then update our matching status
        self.matched[match_type.value] = is_matching
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
                self.root.image_controller.get_images_matched_to(MatchType.RENDER),
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
        if not self.file_type == "fits":
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
            self.limits = Render.get_limits(self.fig, self.image_wcs)

            self.update_matched_images()

    def update_matched_images(self):
        for image in self.root.image_controller.get_images_matched_to(MatchType.COORD):
            if image == self:
                continue

            image.set_limits(self.limits)

    def toggle_grid_lines(self):
        self.grid_lines = not self.grid_lines

        Render.set_grid_lines(self.fig, self.grid_lines)
        self.canvas.draw()

        return self.grid_lines

    def get_ra_dec(self, event):
        if not self.fig.canvas.toolbar.mode == "":
            return

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

    def show_context_menu(self, event):
        self.context_menu = ImageContextMenu(self, self)
        self.context_menu.post(event.x_root, event.y_root)

    def is_within_image_bounds(self, event):
        # Assuming you have stored image's width and height as self.image_width and self.image_height
        # Get the shape of the array from AxesImage
        self.image_height, self.image_width = self.image.get_array().shape[:2]
        return 0 <= event.x <= self.image_width and 0 <= event.y <= self.image_height

    def on_right_click(self, event):
        if self.is_within_image_bounds(event):
            self.show_context_menu(event)


class ImageContextMenu(tk.Menu):
    def __init__(self, parent, image_frame):
        super().__init__(parent, tearoff=0)
        self.image_frame = image_frame

        self.add_command(label="Copy WCS Coords", command=self.copy_wcs_coords)
        self.add_command(label="Copy Image Coords", command=self.copy_image_coords)

    def copy_wcs_coords(self):
        wcs_coords = self.get_wcs_coordinates(
            self.image_frame.image_data_header, self.get_current_pointer_position()
        )
        if wcs_coords:
            self.copy_to_clipboard(wcs_coords)

    def copy_image_coords(self):
        image_coords = self.get_image_coordinates(
            self.image_frame.image_wcs, self.get_current_pointer_position()
        )
        if image_coords:
            self.copy_to_clipboard(image_coords)

    def get_current_pointer_position(self):
        # Return the current position of the pointer within the canvas
        return (
            self.image_frame.canvas.get_tk_widget().winfo_pointerx(),
            self.image_frame.canvas.get_tk_widget().winfo_pointery(),
        )

    def get_wcs_coordinates(self, image_data_header, position):
        if image_data_header:
            x_coord, y_coord = position
            try:
                wcs_ra = image_data_header["CRVAL1"]
                wcs_dec = image_data_header["CRVAL2"]
                wcs_coords = f"RA: {wcs_ra}, Dec: {wcs_dec}"
                return f"WCS Coordinates at (X={x_coord}, Y={y_coord}): {wcs_coords}"
            except KeyError:
                return "WCS Coordinates: N/A"
        else:
            return "WCS Coordinates: N/A"

    def get_image_coordinates(self, image_wcs, position):
        if image_wcs:
            x_coord, y_coord = position
            try:
                img_x, img_y = image_wcs.pixel_to_world_values(x_coord, y_coord)
                return f"Image Coordinates at (X={x_coord}, Y={y_coord}): X={img_x}, Y={img_y}"
            except (AttributeError, ValueError):
                return "Image Coordinates: N/A"
        else:
            return "Image Coordinates: N/A"

    def copy_to_clipboard(self, text):
        # Implement the logic to copy text to the clipboard
        self.image_frame.clipboard_clear()
        self.image_frame.clipboard_append(text)
        self.image_frame.update()  # Now it stays on the clipboard after the window is closed
