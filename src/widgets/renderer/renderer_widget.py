import tkinter as tk
from functools import partial
from typing import TYPE_CHECKING, Optional

import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import src.widgets.image.image_controller as ic
import src.widgets.renderer.histogram_context_menu as hcm
from src import constants
from src._overrides.matplotlib.HistogramToolbar import HistogramToolbar
from src.enums import DataType, Matching, Scaling
from src.lib.util import get_size_inches
from src.widgets.base_widget import BaseWidget
from src.widgets.renderer import histogram

if TYPE_CHECKING:
    from src.widgets.image.image_frame import ImageFrame

# The options in the Scaling dropdown. Add to the Scaling enum
#   if you'd like more options.
scaling_options = [x.value for x in Scaling]

colour_map_options = [
    "viridis",
    "plasma",
    "inferno",
    "magma",
    "cividis",
    "Greys",
    "Purples",
    "Blues",
    "Greens",
    "Oranges",
    "Reds",
    "binary",
    "hot",
]

NO_IMAGE_OPEN = "No image open"


class RendererWidget(BaseWidget):
    label = "Renderer Configuration"
    dropdown = True

    def __init__(self, root):
        super().__init__(root)

        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.toolbar: Optional[HistogramToolbar] = None
        self.context_menu: Optional[hcm.HistogramContextMenu] = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.render_options()
        self.create_histogram()

        ic.selected_image_eh.add(self.on_image_change)
        self.on_image_change(ic.get_selected_image())

    def create_histogram(self):
        self.histogram_main_frame = tb.Frame(self, bootstyle="light")
        self.histogram_main_frame.grid(
            column=0, row=0, sticky=tk.NSEW, padx=10, pady=10
        )
        self.histogram_main_frame.grid_rowconfigure(0, weight=0)
        self.histogram_main_frame.grid_rowconfigure(1, weight=1)

        self.histogram_buttons()
        self.root.update()
        self.histogram_graph()

    def histogram_buttons(self):
        self.percentile_buttons = {}
        for col, percentile in enumerate([*constants.PERCENTILES, "Custom"]):
            text = f"{percentile}%" if percentile != "Custom" else percentile
            self.histogram_main_frame.grid_columnconfigure(col, weight=0)
            self.percentile_buttons[percentile] = tb.Button(
                self.histogram_main_frame,
                text=text,
                bootstyle="dark",
                command=partial(self.set_percentile, str(percentile)),
            )
            self.percentile_buttons[percentile].grid(
                column=col, row=0, sticky=tk.NSEW, padx=10, pady=10
            )

        self.update_percentile_buttons()

    def update_percentile_buttons(self):
        for percentile, button in self.percentile_buttons.items():
            button.configure(bootstyle="dark")

            if self.check_if_image_selected() and (
                str(percentile) == ic.get_selected_image().selected_percentile
            ):
                button.configure(bootstyle="medium")

    def histogram_graph(self):
        self.histogram_frame = tb.Frame(self.histogram_main_frame, bootstyle="light")
        self.histogram_frame.grid_rowconfigure(0, weight=1)
        self.histogram_frame.grid_columnconfigure(0, weight=1)

        self.histo_fig = histogram.create_histogram_graph()
        self.canvas = FigureCanvasTkAgg(self.histo_fig, master=self.histogram_frame)
        self.canvas.get_tk_widget().grid(column=0, row=0, sticky=tk.NSEW)
        self.canvas.mpl_connect("button_press_event", self.on_histo_click)
        self.canvas.draw()

        self.toolbar = HistogramToolbar(self.canvas, self.histogram_frame, pack=False)
        self.toolbar.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        self.toolbar.update()

        self.root.update()

        self.histo_fig.set_size_inches(*get_size_inches(self.canvas.get_tk_widget()))

    def update_histogram_graph(self):
        if not self.check_if_image_selected():
            self.histogram_frame.grid_forget()
            return

        c = len(constants.PERCENTILES) + 1
        self.histogram_frame.grid(
            column=0, columnspan=c, row=1, sticky=tk.NSEW, padx=10, pady=(10, 0)
        )

        image_selected = ic.get_selected_image()

        self.histo_fig = histogram.draw_histogram_graph(
            self.histo_fig,
            image_selected.histo_counts,
            image_selected.histo_bins,
            image_selected.vmin,
            image_selected.vmax,
        )
        self.canvas.draw()

    def update_histogram_lines(self):
        if not self.check_if_image_selected():
            return

        image_selected = ic.get_selected_image()

        self.histo_fig = histogram.draw_histogram_lines(
            self.histo_fig,
            image_selected.vmin,
            image_selected.vmax,
        )
        self.canvas.draw()

    def render_options(self):
        render = tb.Frame(self, width=100, bootstyle="light")
        render.grid(column=1, row=0, sticky=tk.NSEW, padx=10, pady=10)

        label = tb.Label(render, text="Render Options", bootstyle="inverse-light")
        label.grid(column=0, columnspan=2, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.min_entry = self.custom_options(render, "Min", 0, 1)
        self.max_entry = self.custom_options(render, "Max", 0, 2)

        self.scaling_dropdown = self.dropdown_options(
            render,
            "Scaling",
            scaling_options,
            self.on_select_scaling,
            0,
            3,
        )
        self.colour_map_dropdown = self.dropdown_options(
            render,
            "Colour Map",
            colour_map_options,
            self.on_select_colour_map,
            0,
            4,
        )

        grid_lines_lbl = tb.Label(render, bootstyle="inverse-light", text="Grid Lines")
        grid_lines_lbl.grid(column=0, row=5, sticky=tk.NSEW, padx=10, pady=10)

        self.grid_lines_state = tk.BooleanVar()
        self.grid_lines_cbtn = tb.Checkbutton(
            render,
            bootstyle="primary-round-toggle",
            text=None,
            command=self.on_grid_lines,
            variable=self.grid_lines_state,
        )
        self.grid_lines_cbtn.grid(row=5, column=1, sticky=tk.W, padx=10, pady=10)
        self.set_grid_lines_box_state(None)

    def custom_options(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        entry = tb.Entry(parent, bootstyle="dark")
        entry.bind("<FocusOut>", self.on_entry_focusout)
        entry.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        entry.configure(state="disabled")

        return entry

    def dropdown_options(self, parent, text, options, func, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown = tb.Menubutton(parent, text=NO_IMAGE_OPEN, bootstyle="dark")
        dropdown.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        dropdown_menu = tk.Menu(dropdown, tearoff=0)

        for option in options:
            dropdown_menu.add_command(label=option, command=partial(func, option))

        dropdown["menu"] = dropdown_menu

        return dropdown

    # These four functions update state of the UI with the new elements,
    #   and will update the image data, but will not re-render the image
    def set_scaling(self, option: Optional[Scaling]):
        """Update the current selected scaling in the dropdown, and update the image."""
        if option is None:
            self.scaling_dropdown["text"] = NO_IMAGE_OPEN
            return

        self.scaling_dropdown["text"] = option.label

        if not self.check_if_image_selected():
            return

        ic.get_selected_image().set_scaling(option)

    def set_colour_map(self, option):
        if option is None:
            self.colour_map_dropdown["text"] = NO_IMAGE_OPEN
            return

        self.colour_map_dropdown["text"] = option

        if not self.check_if_image_selected():
            return

        ic.get_selected_image().set_colour_map(option)

    def set_vmin_vmax(self, image):
        # Update entries with new percentiles, from cached
        self.min_entry.delete(0, tk.END)
        self.max_entry.delete(0, tk.END)

        if image is not None:
            self.min_entry.configure(state="enabled")
            self.max_entry.configure(state="enabled")
            self.min_entry.insert(0, str(image.vmin))
            self.max_entry.insert(0, str(image.vmax))
        else:
            self.min_entry.configure(state="disabled")
            self.max_entry.configure(state="disabled")

    def set_percentile(self, percentile):
        if not self.check_if_image_selected():
            return

        if percentile is None:
            self.set_vmin_vmax(None)
            self.update_percentile_buttons()
            return

        selected_image = ic.get_selected_image()
        selected_image.set_selected_percentile(percentile)
        self.update_percentile_buttons()
        self.set_vmin_vmax(selected_image)
        self.update_histogram_lines()
        ic.get_selected_image().update_norm()

        self.update_matched_images()

    def set_grid_lines_box_state(self, state: Optional[bool]):
        """
        Set the state of the checkbox to the given state.

        :param state: the state to set it to
        """

        self.grid_lines_cbtn.configure(state="enabled")
        self.grid_lines_state.set(True if state else False)

        if state is None:
            self.grid_lines_cbtn.configure(state="disabled")

    def on_grid_lines(self):
        image = ic.get_selected_image()
        if image is None:
            self.set_grid_lines_box_state(None)
            return

        state = image.toggle_grid_lines()
        self.set_grid_lines_box_state(state)

        self.update_matched_images()

    # These functions listen to events and behave accordingly
    def on_select_scaling(self, option: str):
        if not self.check_if_image_selected():
            return

        self.set_scaling(Scaling.from_str(option))
        ic.get_selected_image().update_norm()

        self.update_matched_images()

        self.root.update()

    def on_select_colour_map(self, option):
        if not self.check_if_image_selected():
            return

        self.set_colour_map(option)
        ic.get_selected_image().update_colour_map()

        self.update_matched_images()

        self.root.update()

    def on_entry_focusout(self, event):
        if not self.check_if_image_selected():
            return

        vmin = float(self.min_entry.get())
        vmax = float(self.max_entry.get())
        ic.get_selected_image().set_vmin_vmax_custom(vmin, vmax)
        self.update_percentile_buttons()
        ic.get_selected_image().update_norm()
        self.update_matched_images()
        self.update_histogram_lines()
        self.root.update()

    def on_image_change(self, image: "ImageFrame"):
        if image is None or image.data_type != DataType.FITS:
            self.set_scaling(None)
            self.set_colour_map(None)
            self.set_percentile(None)
            self.set_vmin_vmax(None)
            self.update_percentile_buttons()
            self.update_histogram_graph()
            self.set_grid_lines_box_state(None)
            return

        self.update_percentile_buttons()
        self.set_vmin_vmax(image)
        self.set_scaling(image.scaling)
        self.set_colour_map(image.colour_map)
        self.update_histogram_graph()
        self.set_grid_lines_box_state(image.grid_lines)

        self.root.update()

    def on_histo_click(self, event):
        if self.histo_fig.canvas.toolbar.mode != "":
            return

        # this is a matplotlib event, so we don't have the access to the x/y for the context menu position
        # (the pointer)
        # so grab it manually
        window_x, window_y = (
            self.canvas.get_tk_widget().winfo_pointerx(),
            self.canvas.get_tk_widget().winfo_pointery(),
        )

        ax = self.histo_fig.axes[0]
        if ax == event.inaxes and event.button == 3:
            # transform from position on the canvas to image position
            image_x, _ = ax.transData.inverted().transform((event.x, event.y))
            self.show_context_menu(event, image_x, window_x, window_y)

    def show_context_menu(self, _event, image_x: float, window_x: int, window_y: int):
        self.context_menu = hcm.HistogramContextMenu(self, image_x)
        self.context_menu.post(window_x, window_y)

    def check_if_image_selected(self):
        image = ic.get_selected_image()
        return image is not None and image.data_type == DataType.FITS

    def update_matched_images(self):
        if not ic.get_selected_image().is_matched(Matching.RENDER):
            return

        for image in ic.get_images_matched_to(Matching.RENDER):
            if image == ic.get_selected_image():
                continue

            image.match_render(ic.get_selected_image())

    def close(self):
        ic.selected_image_eh.remove(self.on_image_change)

        super().close()
